from abc import ABC, abstractmethod
from typing import Dict, Any
from vault_injector.destinations.models import DBTypeSecret
import hvac
import loguru
import os


class Destination(ABC):
    def __init__(self):
        self.url = self._get_url()
        self.token = self._get_token()
        self.client = hvac.Client(url=self.url, token=self.token)

    @staticmethod
    def _get_url():
        return os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")

    @staticmethod
    def _get_token():
        return os.getenv("VAULT_TOKEN", "root")

    @staticmethod
    def _get_unseal_keys():
        return os.getenv("VAULT_UNSEAL_KEYS", "").split(",")

    def is_authenticated(self) -> bool:
        """
        Check if the vault is authenticated.
        """
        try:
            return self.client.is_authenticated()
        except hvac.exceptions.VaultDown as e:
            loguru.logger.error(f"Vault is down: {e}", exc_info=True)
            return False

    def unseal_vault(self):
        """
        Unseal the vault if it is sealed.
        """
        if not self.is_authenticated():
            root_token_used = False
            # current_unseal_key_index = 0
            unseal_keys = self._get_unseal_keys()
            while self.client.seal_status.get("sealed", False):
                if not root_token_used:
                    self.client.sys.submit_unseal_keys(keys=unseal_keys)

        return True

    def __enter__(self):
        # if not self.client.is_authenticated():
        #     self.client.auth.unseal_vault()
        if not self.is_authenticated():
            self.unseal_vault()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self.client, "logout"):
            self.client.logout()
        self.client = None  # Clear the client to make object unusable

    @abstractmethod
    def add_secret(self, data: Dict[str, Any]):
        raise NotImplementedError

    def ping(self) -> bool:
        """
        Ping the destination to check if it is reachable.
        """
        if self.client is None:
            loguru.logger.error("Vault client has been closed")
            return False

        return self.is_authenticated()

    def seal_vault(self):
        self.client.sys.seal()
        
    def get_enabled_secrets(self) -> list[str]:
        """
        Get a list of enabled secrets.
        """
        return list(self.client.sys.list_mounted_secrets_engines()["data"].keys())
    
class DBDestination(Destination):
    """
    Database Related Secrets,
    - store database related secrets
    - get new ephermal secret vault from existing secrets.
    """
    DB_MAPPING = {
        "postgres": {
            "db_name": "postgresql", "plugin_name": "postgresql-database-plugin", 
            "config": {
                "connection_url": "postgresql://{{{{username}}}}:{{{{password}}}}@{host}:{port}/{database}?sslmode={sslmode}", 
                "role_name": "readonly-pg",
                "allowed_roles": "*", "default_lease_ttl": "12h", "max_lease_ttl": "24h"}},
        "mysql": {"db_name": "mysql", "plugin_name": "mysql-database-plugin", "config": {"connection_url": "mysql://{username}:{password}@{host}:{port}/{database}", "allowed_roles": "*", "default_lease_ttl": "12h", "max_lease_ttl": "24h"}},
    }

    def __init__(self):
        super().__init__()

        
    def setup(self, config: Dict[str, Any]):    
        self._enable_db_secret(backend_type="database", path=config["path"], db_name=config["db_name"])
        

    def _enable_db_secret(self, backend_type: str, path: str, db_name: str) -> bool:
        """
        Enable the database secret engine.
        """
        if db_name not in self.DB_MAPPING:
            raise ValueError(f"Database not supported: {db_name}, Supported databases: {list(self.DB_MAPPING.keys())}")
        print(self.get_enabled_secrets())
        if f"{path}/" not in self.get_enabled_secrets():
            print(f"Data: {self.DB_MAPPING[db_name]}")
            self.client.sys.enable_secrets_engine(backend_type=backend_type, path=path, plugin_name=self.DB_MAPPING[db_name]["plugin_name"])
            # self.client.sys.enable_secrets_engine(backend_type=backend_type,  plugin_name=self.DB_MAPPING[db_name]["plugin_name"])
        return True

    def add_secret(self, data: DBTypeSecret):
        res = self.client.write_data(path=data.secret_path, data=data.secret_data.model_dump())
        return res
    
    def get_secrets(self, path: str) -> DBTypeSecret:
        """
        Get a new ephermal secret from the database.
        """
        return None
        # existing_secrets = self.get_data()
        # if not existing_secrets:
        #     raise ValueError("No existing secrets found")
        # return DBTypeSecret(
        #     secret_path=existing_secrets[0].secret_path,
        #     secret_data=existing_secrets[0].secret_data,
        # )

    def create_readonly_role(self, mount_point:str, config: DBTypeSecret):
        connection_url = self.DB_MAPPING[config.db_engine]["config"]["connection_url"].format(
            username=config.secret_data.username, password=config.secret_data.password, 
            host=config.secret_data.host, port=config.secret_data.port, 
            database=config.secret_data.database, 
            sslmode=config.secret_data.sslmode)
        try:
            res = self.client.secrets.database.configure(
                name=config.db_engine,
                mount_point=mount_point,
                plugin_name=self.DB_MAPPING[config.db_engine]["plugin_name"],
                allowed_roles=self.DB_MAPPING[config.db_engine]["config"]["role_name"],
                connection_url=connection_url,
                username=config.secret_data.username,
                password=config.secret_data.password,
            )
        except Exception as e:
            loguru.logger.error(f"Error creating readonly role: {e}", exc_info=True)
            return False
        return res.status_code == 204

    def create_connection(self, config: DBTypeSecret):
        self.client.secrets.database.create_connection(
            name=config.secret_data.database,
            plugin_name=self.DB_MAPPING[config.secret_data.database]["plugin_name"],
            connection_url=self.DB_MAPPING[config.secret_data.database]["config"]["connection_url"].format(username=config.secret_data.username, password=config.secret_data.password, host=config.secret_data.host, port=config.secret_data.port, database=config.secret_data.database, sslmode="disable")
        )
        return True