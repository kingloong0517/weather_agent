from fastapi import APIRouter
from app.agents.llm_agent import LLMAgent
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()
weather_agent = LLMAgent()


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


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def stream_response():
        # 执行 Agent 的流式方法
        async for chunk in weather_agent.execute_stream(request.query):
            data = json.dumps(chunk)
            yield f"data: {data}\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")
