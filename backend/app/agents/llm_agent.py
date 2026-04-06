from typing import Any, Dict, List
from .base import BaseAgent
from app.nlp.processor import NLUProcessor
from app.tools import weather_tool, schedule_tool
from app.llm.client import call_llm, call_llm_async, call_llm_async_stream
import json
import asyncio


class LLMAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="LLMAgent")
        self.nlu_processor = NLUProcessor()
    
    def execute(self, query: str) -> Dict[str, Any]:
        # 1. 调用意图识别模块
        nlu_result = self.nlu_processor.process(query)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        
        # 2. 定义可用工具
        available_tools = [
            {
                "name": "weather_tool",
                "description": "查询指定日期和地点的天气信息",
                "parameters": {
                    "date": "日期，如'今天'、'明天'、'后天'",
                    "location": "地点，如'北京'、'上海'、'广州'"
                }
            },
            {
                "name": "schedule_tool",
                "description": "设置日程提醒",
                "parameters": {
                    "time": "时间，如'今天下午3点'、'明天上午9点'",
                    "event": "事件，如'开会'、'吃饭'、'购物'"
                }
            }
        ]
        
        # 3. 构建 prompt 让大模型按照 ReAct 格式输出
        tools_str = "\n".join([f"- {tool['name']}: {tool['description']}，参数：{tool['parameters']}" for tool in available_tools])
        
        prompt = "请按照 ReAct 格式回答用户问题。\n\n"
        prompt += f"用户输入：{query}\n\n"
        prompt += "可用工具：\n"
        prompt += tools_str + "\n\n"
        prompt += "输出格式：\n"
        prompt += "Thought: 你的思考过程\n"
        prompt += "Action: 工具名称\n"
        prompt += "Action Input: {\"参数名\": \"参数值\"}\n\n"
        prompt += "然后我会执行工具并返回结果，你需要根据结果生成最终回答。\n\n"
        prompt += "示例1：\n"
        prompt += "用户输入：北京明天天气怎么样\n\n"
        prompt += "Thought: 用户在问北京明天的天气，我需要调用天气工具来查询\n"
        prompt += "Action: weather_tool\n"
        prompt += "Action Input: {\"date\": \"明天\", \"location\": \"北京\"}\n\n"
        prompt += "示例2：\n"
        prompt += "用户输入：提醒我明天下午3点开会\n\n"
        prompt += "Thought: 用户需要设置明天下午3点的会议提醒，我需要调用日程工具\n"
        prompt += "Action: schedule_tool\n"
        prompt += "Action Input: {\"time\": \"明天下午3点\", \"event\": \"开会\"}\n\n"
        prompt += "示例3：\n"
        prompt += "用户输入：你好\n\n"
        prompt += "Thought: 用户在打招呼，不需要调用工具\n"
        prompt += "Action: none\n"
        prompt += "Action Input: {}\n"
        
        tool_calls: List[Dict[str, Any]] = []
        final_answer = ""
        
        react_steps = []
        
        try:
            # 调用大模型获取 ReAct 格式输出
            response = call_llm(prompt)
            print(f"LLM ReAct 响应: {response}")
            
            # 检查是否是错误信息
            if response.startswith("错误:"):
                print(f"LLM 调用失败: {response}")
                # Fallback 到原有的规则驱动逻辑
                if intent == "weather_query":
                    # 提取实体
                    location = entities.get("location", "北京")
                    date = entities.get("date", "今天")
                    
                    # 记录思考过程
                    react_steps.append({
                        "type": "thought",
                        "content": f"用户询问{location}{date}的天气，需要查询天气工具"
                    })
                    
                    # 记录动作
                    react_steps.append({
                        "type": "action",
                        "content": "调用工具: weather_tool",
                        "tool": "weather_tool",
                        "params": {"date": date, "location": location}
                    })
                    
                    # 调用天气工具
                    weather_result = weather_tool(date, location)
                    
                    # 记录观察结果
                    observation = f"{date}{location}的天气：{weather_result['weather']}"
                    react_steps.append({
                        "type": "observation",
                        "content": observation,
                        "result": weather_result
                    })
                    
                    # 构建工具调用记录
                    tool_calls.append({
                        "tool": "weather_tool",
                        "params": {"date": date, "location": location},
                        "result": weather_result["weather"]
                    })
                    
                    # 生成最终回答
                    final_answer = f"{date}{location}的天气情况：{weather_result['weather']}，{weather_result['advice']}"
                    
                elif intent == "schedule_reminder":
                    # 提取实体
                    date = entities.get("date", "今天")
                    time = entities.get("time", "")
                    event = entities.get("event", "事件")
                    
                    # 记录思考过程
                    react_steps.append({
                        "type": "thought",
                        "content": f"用户需要设置{date}{time}的{event}提醒，需要调用日程工具"
                    })
                    
                    # 记录动作
                    react_steps.append({
                        "type": "action",
                        "content": "调用工具: schedule_tool",
                        "tool": "schedule_tool",
                        "params": {"time": f"{date}{time}", "event": event}
                    })
                    
                    # 调用日程工具
                    schedule_result = schedule_tool(f"{date}{time}", event)
                    
                    # 记录观察结果
                    observation = f"已设置提醒: {event} - {date}{time}"
                    react_steps.append({
                        "type": "observation",
                        "content": observation,
                        "result": schedule_result
                    })
                    
                    # 构建工具调用记录
                    tool_calls.append({
                        "tool": "schedule_tool",
                        "params": {"time": f"{date}{time}", "event": event},
                        "result": schedule_result["status"]
                    })
                    
                    # 生成最终回答
                    final_answer = schedule_result["message"]
                    
                else:
                    final_answer = "抱歉，我不理解您的意思"
            else:
                # 解析 ReAct 格式
                lines = response.strip().split('\n')
                thought = ""
                action = ""
                action_input = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Thought:"):
                        thought = line[8:].strip()
                    elif line.startswith("Action:"):
                        action = line[7:].strip()
                    elif line.startswith("Action Input:"):
                        # 提取并解析 Action Input
                        input_str = line[13:].strip()
                        try:
                            action_input = json.loads(input_str)
                        except:
                            action_input = {}
                
                # 记录思考过程
                if thought:
                    react_steps.append({
                        "type": "thought",
                        "content": thought
                    })
                
                # 执行工具调用
                if action and action != "none":
                    # 记录动作
                    react_steps.append({
                        "type": "action",
                        "content": f"调用工具: {action}",
                        "tool": action,
                        "params": action_input
                    })
                    
                    if action == "weather_tool":
                        # 调用天气工具
                        date = action_input.get("date", "今天")
                        location = action_input.get("location", "北京")
                        weather_result = weather_tool(date, location)
                        
                        # 记录观察结果
                        observation = f"{date}{location}的天气：{weather_result['weather']}"
                        react_steps.append({
                            "type": "observation",
                            "content": observation,
                            "result": weather_result
                        })
                        
                        # 构建工具调用记录
                        tool_calls.append({
                            "tool": "weather_tool",
                            "params": {"date": date, "location": location},
                            "result": weather_result["weather"]
                        })
                        
                        # 生成最终回答
                        final_answer = f"{date}{location}的天气情况：{weather_result['weather']}，{weather_result['advice']}"
                        
                    elif action == "schedule_tool":
                        # 调用日程工具
                        time = action_input.get("time", "今天")
                        event = action_input.get("event", "事件")
                        schedule_result = schedule_tool(time, event)
                        
                        # 记录观察结果
                        observation = f"已设置提醒: {event} - {time}"
                        react_steps.append({
                            "type": "observation",
                            "content": observation,
                            "result": schedule_result
                        })
                        
                        # 构建工具调用记录
                        tool_calls.append({
                            "tool": "schedule_tool",
                            "params": {"time": time, "event": event},
                            "result": schedule_result["status"]
                        })
                        
                        # 生成最终回答
                        final_answer = schedule_result["message"]
                else:
                    # 不需要调用工具，直接生成回答
                    final_answer = "你好！我是天气 Agent，有什么可以帮您的吗？"
                
        except Exception as e:
            print(f"LLM ReAct 解析失败: {e}")
            # Fallback 到原有的规则驱动逻辑
            if intent == "weather_query":
                # 提取实体
                location = entities.get("location", "北京")
                date = entities.get("date", "今天")
                
                # 记录思考过程
                react_steps.append({
                    "type": "thought",
                    "content": f"用户询问{location}{date}的天气，需要查询天气工具"
                })
                
                # 记录动作
                react_steps.append({
                    "type": "action",
                    "content": "调用工具: weather_tool",
                    "tool": "weather_tool",
                    "params": {"date": date, "location": location}
                })
                
                # 调用天气工具
                weather_result = weather_tool(date, location)
                
                # 记录观察结果
                observation = f"{date}{location}的天气：{weather_result['weather']}"
                react_steps.append({
                    "type": "observation",
                    "content": observation,
                    "result": weather_result
                })
                
                # 构建工具调用记录
                tool_calls.append({
                    "tool": "weather_tool",
                    "params": {"date": date, "location": location},
                    "result": weather_result["weather"]
                })
                
                # 生成最终回答
                final_answer = f"{date}{location}的天气情况：{weather_result['weather']}，{weather_result['advice']}"
                
            elif intent == "schedule_reminder":
                # 提取实体
                date = entities.get("date", "今天")
                time = entities.get("time", "")
                event = entities.get("event", "事件")
                
                # 记录思考过程
                react_steps.append({
                    "type": "thought",
                    "content": f"用户需要设置{date}{time}的{event}提醒，需要调用日程工具"
                })
                
                # 记录动作
                react_steps.append({
                    "type": "action",
                    "content": "调用工具: schedule_tool",
                    "tool": "schedule_tool",
                    "params": {"time": f"{date}{time}", "event": event}
                })
                
                # 调用日程工具
                schedule_result = schedule_tool(f"{date}{time}", event)
                
                # 记录观察结果
                observation = f"已设置提醒: {event} - {date}{time}"
                react_steps.append({
                    "type": "observation",
                    "content": observation,
                    "result": schedule_result
                })
                
                # 构建工具调用记录
                tool_calls.append({
                    "tool": "schedule_tool",
                    "params": {"time": f"{date}{time}", "event": event},
                    "result": schedule_result["status"]
                })
                
                # 生成最终回答
                final_answer = schedule_result["message"]
                
            else:
                final_answer = "抱歉，我不理解您的意思"
        
        # 4. 返回完整执行链
        return {
            "user_input": query,
            "intent": intent,
            "tool_calls": tool_calls,
            "final_answer": final_answer,
            "react_steps": react_steps
        }
    
    async def execute_stream(self, query: str):
        """
        流式执行 Agent 流程，实时产生输出
        """
        try:
            # 1. 调用意图识别模块
            nlu_result = self.nlu_processor.process(query)
            intent = nlu_result["intent"]
            entities = nlu_result["entities"]
            
            # 发送意图识别结果
            yield {
                "type": "intent",
                "data": intent
            }
            await asyncio.sleep(0.5)
            
            # 2. 定义可用工具
            available_tools = [
                {
                    "name": "weather_tool",
                    "description": "查询指定日期和地点的天气信息",
                    "parameters": {
                        "date": "日期，如'今天'、'明天'、'后天'",
                        "location": "地点，如'北京'、'上海'、'广州'"
                    }
                },
                {
                    "name": "schedule_tool",
                    "description": "设置日程提醒",
                    "parameters": {
                        "time": "时间，如'今天下午3点'、'明天上午9点'",
                        "event": "事件，如'开会'、'吃饭'、'购物'"
                    }
                }
            ]
            
            # 3. 构建 prompt 让大模型按照 ReAct 格式输出
            tools_str = "\n".join([f"- {tool['name']}: {tool['description']}，参数：{tool['parameters']}" for tool in available_tools])
            
            prompt = "请按照 ReAct 格式回答用户问题。\n\n"
            prompt += f"用户输入：{query}\n\n"
            prompt += "可用工具：\n"
            prompt += tools_str + "\n\n"
            prompt += "输出格式：\n"
            prompt += "Thought: 你的思考过程\n"
            prompt += "Action: 工具名称\n"
            prompt += "Action Input: {\"参数名\": \"参数值\"}\n\n"
            prompt += "然后我会执行工具并返回结果，你需要根据结果生成最终回答。\n\n"
            prompt += "示例1：\n"
            prompt += "用户输入：北京明天天气怎么样\n\n"
            prompt += "Thought: 用户在问北京明天的天气，我需要调用天气工具来查询\n"
            prompt += "Action: weather_tool\n"
            prompt += "Action Input: {\"date\": \"明天\", \"location\": \"北京\"}\n\n"
            prompt += "示例2：\n"
            prompt += "用户输入：提醒我明天下午3点开会\n\n"
            prompt += "Thought: 用户需要设置明天下午3点的会议提醒，我需要调用日程工具\n"
            prompt += "Action: schedule_tool\n"
            prompt += "Action Input: {\"time\": \"明天下午3点\", \"event\": \"开会\"}\n\n"
            prompt += "示例3：\n"
            prompt += "用户输入：你好\n\n"
            prompt += "Thought: 用户在打招呼，不需要调用工具\n"
            prompt += "Action: none\n"
            prompt += "Action Input: {}\n"
            
            # 发送正在思考的消息
            yield {
                "type": "react_step",
                "data": {
                    "type": "thought",
                    "content": "正在分析用户意图，思考如何响应..."
                }
            }
            await asyncio.sleep(0.5)
            
            # 调用大模型获取 ReAct 格式输出（流式）
            response_content = ""
            error_occurred = False
            
            async for chunk in call_llm_async_stream(prompt):
                response_content += chunk
                # 检查是否是错误信息
                if chunk.startswith("错误:"):
                    error_occurred = True
                    break
            
            print(f"LLM ReAct 响应: {response_content}")
            
            # 检查是否是错误信息或空响应
            if error_occurred or response_content.startswith("错误:") or not response_content.strip():
                print(f"LLM 调用失败: {response_content}")
                # Fallback 到原有的规则驱动逻辑
                if intent == "weather_query":
                    # 提取实体
                    location = entities.get("location", "北京")
                    date = entities.get("date", "今天")
                    
                    # 发送思考过程
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "thought",
                            "content": f"用户询问{location}{date}的天气，需要查询天气工具"
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 发送动作
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "action",
                            "content": "调用工具: weather_tool",
                            "tool": "weather_tool",
                            "params": {"date": date, "location": location}
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 调用天气工具
                    weather_result = weather_tool(date, location)
                    
                    # 发送观察结果
                    observation = f"{date}{location}的天气：{weather_result['weather']}"
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "observation",
                            "content": observation,
                            "result": weather_result
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 发送工具调用
                    yield {
                        "type": "tool_call",
                        "data": {
                            "tool": "weather_tool",
                            "params": {"date": date, "location": location},
                            "result": weather_result["weather"]
                        }
                    }
                    await asyncio.sleep(0.5)
                    
                    # 发送最终回答
                    final_answer = f"{date}{location}的天气情况：{weather_result['weather']}，{weather_result['advice']}"
                    yield {
                        "type": "final_answer",
                        "data": final_answer
                    }
                    await asyncio.sleep(0.3)
                    
                elif intent == "schedule_reminder":
                    # 提取实体
                    date = entities.get("date", "今天")
                    time = entities.get("time", "")
                    event = entities.get("event", "事件")
                    
                    # 发送思考过程
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "thought",
                            "content": f"用户需要设置{date}{time}的{event}提醒，需要调用日程工具"
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 发送动作
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "action",
                            "content": "调用工具: schedule_tool",
                            "tool": "schedule_tool",
                            "params": {"time": f"{date}{time}", "event": event}
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 调用日程工具
                    schedule_result = schedule_tool(f"{date}{time}", event)
                    
                    # 发送观察结果
                    observation = f"已设置提醒: {event} - {date}{time}"
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "observation",
                            "content": observation,
                            "result": schedule_result
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    # 发送工具调用
                    yield {
                        "type": "tool_call",
                        "data": {
                            "tool": "schedule_tool",
                            "params": {"time": f"{date}{time}", "event": event},
                            "result": schedule_result["status"]
                        }
                    }
                    await asyncio.sleep(0.5)
                    
                    # 发送最终回答
                    final_answer = schedule_result["message"]
                    yield {
                        "type": "final_answer",
                        "data": final_answer
                    }
                    await asyncio.sleep(0.3)
                    
                else:
                    # 发送最终回答
                    yield {
                        "type": "final_answer",
                        "data": "抱歉，我不理解您的意思"
                    }
                    await asyncio.sleep(0.3)
            else:
                # 解析 ReAct 格式
                lines = response_content.strip().split('\n')
                thought = ""
                action = ""
                action_input = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Thought:"):
                        thought = line[8:].strip()
                    elif line.startswith("Action:"):
                        action = line[7:].strip()
                    elif line.startswith("Action Input:"):
                        # 提取并解析 Action Input
                        input_str = line[13:].strip()
                        try:
                            action_input = json.loads(input_str)
                        except:
                            action_input = {}
                
                # 发送思考过程
                if thought:
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "thought",
                            "content": thought
                        }
                    }
                    await asyncio.sleep(0.8)
                
                # 执行工具调用
                if action and action != "none":
                    # 发送动作
                    yield {
                        "type": "react_step",
                        "data": {
                            "type": "action",
                            "content": f"调用工具: {action}",
                            "tool": action,
                            "params": action_input
                        }
                    }
                    await asyncio.sleep(0.8)
                    
                    if action == "weather_tool":
                        # 调用天气工具
                        date = action_input.get("date", "今天")
                        location = action_input.get("location", "北京")
                        weather_result = weather_tool(date, location)
                        
                        # 发送观察结果
                        observation = f"{date}{location}的天气：{weather_result['weather']}"
                        yield {
                            "type": "react_step",
                            "data": {
                                "type": "observation",
                                "content": observation,
                                "result": weather_result
                            }
                        }
                        await asyncio.sleep(0.8)
                        
                        # 发送工具调用
                        yield {
                            "type": "tool_call",
                            "data": {
                                "tool": "weather_tool",
                                "params": {"date": date, "location": location},
                                "result": weather_result["weather"]
                            }
                        }
                        await asyncio.sleep(0.5)
                        
                        # 发送最终回答
                        final_answer = f"{date}{location}的天气情况：{weather_result['weather']}，{weather_result['advice']}"
                        yield {
                            "type": "final_answer",
                            "data": final_answer
                        }
                        await asyncio.sleep(0.3)
                        
                    elif action == "schedule_tool":
                        # 调用日程工具
                        time = action_input.get("time", "今天")
                        event = action_input.get("event", "事件")
                        schedule_result = schedule_tool(time, event)
                        
                        # 发送观察结果
                        observation = f"已设置提醒: {event} - {time}"
                        yield {
                            "type": "react_step",
                            "data": {
                                "type": "observation",
                                "content": observation,
                                "result": schedule_result
                            }
                        }
                        await asyncio.sleep(0.8)
                        
                        # 发送工具调用
                        yield {
                            "type": "tool_call",
                            "data": {
                                "tool": "schedule_tool",
                                "params": {"time": time, "event": event},
                                "result": schedule_result["status"]
                            }
                        }
                        await asyncio.sleep(0.5)
                        
                        # 发送最终回答
                        final_answer = schedule_result["message"]
                        yield {
                            "type": "final_answer",
                            "data": final_answer
                        }
                        await asyncio.sleep(0.3)
                else:
                    # 不需要调用工具，直接发送最终回答
                    yield {
                        "type": "final_answer",
                        "data": "你好！我是天气 Agent，有什么可以帮您的吗？"
                    }
                    await asyncio.sleep(0.3)
                
        except Exception as e:
            print(f"执行失败: {e}")
            import traceback
            traceback.print_exc()
            # 发送错误信息
            yield {
                "type": "final_answer",
                "data": f"执行失败: {str(e)}"
            }
        
        # 发送结束标志
        yield {
            "type": "done"
        }