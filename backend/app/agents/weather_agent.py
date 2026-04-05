from typing import Any, Dict, List
from .base import BaseAgent
from app.nlp.processor import NLUProcessor
from app.tools import weather_tool, schedule_tool


class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="WeatherAgent")
        self.nlu_processor = NLUProcessor()

    def execute(self, query: str) -> Dict[str, Any]:
        # 1. 调用意图识别模块
        nlu_result = self.nlu_processor.process(query)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        
        # 2. 根据 intent 调用对应工具
        tool_calls: List[Dict[str, Any]] = []
        final_answer = ""
        
        if intent == "weather_query":
            # 提取实体
            location = entities.get("location", "北京")
            date = entities.get("date", "今天")
            
            # 调用天气工具
            weather_result = weather_tool(date, location)
            
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
            
            # 调用日程工具
            schedule_result = schedule_tool(f"{date}{time}", event)
            
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
        
        # 3. 返回完整执行链
        return {
            "user_input": query,
            "intent": intent,
            "tool_calls": tool_calls,
            "final_answer": final_answer
        }
