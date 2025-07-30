from abc import ABC, abstractmethod
from typing import List, Dict, Any

from vault_injector.destinations.base import Destination


class Source(ABC):
    def __init__(self, path: str):
        self.path = path

    @abstractmethod
    def get_data(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_data_by_id(self, id: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def put_data(self, data: Dict[str, Any], dest: Destination) -> Dict[str, Any]:
        raise NotImplementedError


class JsonSource(Source):
    def get_data(self) -> List[Dict[str, Any]]:
        return []

    def get_data_by_id(self, id: str) -> Dict[str, Any]:
        return {}

    def put_data(self, data: Dict[str, Any], dest: Destination) -> Dict[str, Any]:
        return {}


class ConsoleSource(Source):
    def get_data(self) -> List[Dict[str, Any]]:
        return []

    def get_data_by_id(self, id: str) -> Dict[str, Any]:
        return {}

    def put_data(self, data: Dict[str, Any], dest: Destination) -> Dict[str, Any]:
        return {}
