from typing import List, Dict, Any
import json

from vault_injector.sources.base import Source
from vault_injector.destinations.base import Destination


class JSONSource(Source):
    """A source that reads and writes data from JSON files."""

    def __init__(self, path: str):
        """Initialize the JSON source with a file path.

        Args:
            path: The path to the JSON file
        """
        super().__init__(path)
        self._data: List[Dict[str, Any]] = []
        self.data = self._load_from_file()

    def _load_from_file(self) -> List[Dict[str, Any]]:
        """Load data from the JSON file.

        Returns:
            List[Dict[str, Any]]: The data loaded from the file
        """
        with open(self.path, "r") as f:
            return json.load(f)

    @property
    def data(self) -> List[Dict[str, Any]]:
        """Get the current data from the JSON source.

        Returns:
            List[Dict[str, Any]]: The current data
        """
        return self._data

    @data.setter
    def data(self, value: List[Dict[str, Any]]) -> None:
        """Set the data in the JSON source.

        Args:
            value: The new data to set
        """
        self._data = value

    def get_data(self) -> List[Dict[str, Any]]:
        return self.data

    def get_data_by_id(self, id: str) -> Dict[str, Any]:
        """Get a specific item from the data by its ID.

        Args:
            id: The ID of the item to retrieve

        Returns:
            Dict[str, Any]: The item with the specified ID
        """
        for item in self._data:
            if item.get("id") == id:
                return item
        return {}

    def put_data(self, data: Dict[str, Any], dest: Destination) -> Dict[str, Any]:
        """Put data into the destination.

        Args:
            data: The data to put
            dest: The destination to put the data into

        Returns:
            Dict[str, Any]: The result of the operation
        """
        # TODO: Implement actual data writing logic
        return {}
