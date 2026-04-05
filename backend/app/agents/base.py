from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.tools: List[Any] = []

    @abstractmethod
    def execute(self, query: str) -> Dict[str, Any]:
        pass

    def add_tool(self, tool: Any) -> None:
        self.tools.append(tool)

    def remove_tool(self, tool_name: str) -> None:
        self.tools = [t for t in self.tools if t.name != tool_name]
