from pydantic import BaseModel
from typing import Any, Dict, Optional


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    query: str
    response: Optional[str] = None
    tool_calls: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolInfo(BaseModel):
    name: str
    description: str
