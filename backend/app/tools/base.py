from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    def get_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description
        }
