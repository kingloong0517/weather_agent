import asyncio
from app.agents.llm_agent import LLMAgent

async def test():
    agent = LLMAgent()
    async for chunk in agent.execute_stream('重庆天气怎么样'):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(test())