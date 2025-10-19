from abc import ABC, abstractmethod
from typing import Dict, Any
from vault_injector.destinations.models import DBData, DBTypeSecret
import hvac


class Destination(ABC):
    def __init__(self, vault_client: hvac.Client):
        self.vault_client = vault_client

    @abstractmethod
    def put_data(self, data: Dict[str, Any]):
        raise NotImplementedError

class DBDestination(ABC):
    """
    Database Related Secrets, 
    - store database related secrets 
    - get new ephermal secret vault from existing secrets.
    """
    def __init__(self, vault_client: hvac.Client):
        super().__init__(vault_client)

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