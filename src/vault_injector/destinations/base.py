from abc import ABC, abstractmethod
from typing import Dict, Any
from vault_injector.destinations.models import DBData, DBTypeSecret
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
        if hasattr(self.client, 'logout'):
            self.client.logout()
        self.client = None  # Clear the client to make object unusable

    @abstractmethod
    def put_data(self, data: Dict[str, Any]):
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

class DBDestination(Destination):
    """
    Database Related Secrets, 
    - store database related secrets 
    - get new ephermal secret vault from existing secrets.
    """
    def __init__(self):
        super().__init__()

    def put_data(self, data: DBData):
        pass
    
    def get_new_secret(self) -> DBTypeSecret:
        """
        Get a new ephermal secret from the database.
        """
        existing_secrets = self.get_data()
        if not existing_secrets:
            raise ValueError("No existing secrets found")
        return DBTypeSecret(
            secret_path=existing_secrets[0].secret_path,
            secret_data=existing_secrets[0].secret_data,
        )