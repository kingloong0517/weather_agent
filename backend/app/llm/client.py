import json
import asyncio
import aiohttp
import requests
from typing import Optional
from app.config import settings


def call_llm(prompt: str) -> str:
    """
    调用大模型 API 生成文本（同步版本）
    
    Args:
        prompt: 提示词文本
        
    Returns:
        模型生成的文本结果
    """
    # 检查 API Key 是否配置
    if not settings.llm_api_key:
        return "错误: LLM API Key 未配置"
    
    # 构建请求数据
    data = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": settings.llm_temperature
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}"
    }
    
    try:
        # 发送请求
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        
        # 检查响应状态
        if response.status_code != 200:
            return f"错误: API 调用失败，状态码: {response.status_code}"
        
        # 解析响应
        result = response.json()
        
        # 提取生成的文本
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "错误: 无法获取模型生成结果"
            
    except Exception as e:
        return f"错误: {str(e)}"


async def call_llm_async(prompt: str) -> str:
    """
    调用大模型 API 生成文本（异步版本）
    
    Args:
        prompt: 提示词文本
        
    Returns:
        模型生成的文本结果
    """
    # 检查 API Key 是否配置
    if not settings.llm_api_key:
        return "错误: LLM API Key 未配置"
    
    # 构建请求数据
    data = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": settings.llm_temperature
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}"
    }
    
    try:
        # 发送异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.llm_base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # 检查响应状态
                if response.status != 200:
                    return f"错误: API 调用失败，状态码: {response.status}"
                
                # 解析响应
                result = await response.json()
                
                # 提取生成的文本
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return "错误: 无法获取模型生成结果"
            
    except Exception as e:
        return f"错误: {str(e)}"


async def call_llm_async_stream(prompt: str):
    """
    调用大模型 API 生成文本（异步流式版本）
    
    Args:
        prompt: 提示词文本
        
    Yields:
        模型生成的文本片段
    """
    # 检查 API Key 是否配置
    if not settings.llm_api_key:
        yield "错误: LLM API Key 未配置"
        return
    
    # 构建请求数据
    data = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": settings.llm_temperature,
        "stream": True  # 启用流式响应
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}"
    }
    
    try:
        # 发送异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.llm_base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # 检查响应状态
                if response.status != 200:
                    yield f"错误: API 调用失败，状态码: {response.status}"
                    return
                
                # 处理流式响应
                async for chunk in response.content:
                    if chunk:
                        # 解码并处理每个chunk
                        chunk_str = chunk.decode('utf-8')
                        # 分割SSE事件
                        events = chunk_str.split('\n\n')
                        for event in events:
                            if event.strip():
                                # 提取data字段
                                lines = event.split('\n')
                                for line in lines:
                                    if line.startswith('data: '):
                                        data_str = line[6:]
                                        if data_str == '[DONE]':
                                            return
                                        try:
                                            data = json.loads(data_str)
                                            if "choices" in data and len(data["choices"]) > 0:
                                                delta = data["choices"][0].get("delta", {})
                                                content = delta.get("content", "")
                                                if content:
                                                    yield content
                                        except json.JSONDecodeError:
                                            pass
    except Exception as e:
        yield f"错误: {str(e)}"


if __name__ == "__main__":
    # 测试 LLM 调用
    test_prompt = "你好，请介绍一下自己"
    result = call_llm(test_prompt)
    print(f"测试结果: {result}")