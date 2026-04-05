from fastapi import APIRouter
from app.agents.weather_agent import WeatherAgent

router = APIRouter()
weather_agent = WeatherAgent()


from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
async def chat(request: ChatRequest):
    # 使用 Agent 调度模块处理请求
    result = weather_agent.execute(request.query)
    
    # 构建响应
    response = {
        "query": request.query,
        "response": result["final_answer"],
        "intent": result["intent"],
        "tool_calls": result["tool_calls"],
        "execution_chain": result
    }
    
    return response
