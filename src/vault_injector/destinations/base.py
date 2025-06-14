from abc import ABC, abstractmethod
from typing import Dict, Any


class Destination(ABC):
    @abstractmethod
    def put_data(self, data: Dict[str, Any]):
        raise NotImplementedError
