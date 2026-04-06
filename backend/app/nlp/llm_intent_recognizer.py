from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from app.nlp.intent_recognizer import IntentRecognizer, IntentResult
from app.llm.client import call_llm


class LLMIntentRecognizer(IntentRecognizer):
    """
    使用大模型进行意图识别
    """
    
    def __init__(self):
        super().__init__()
        
    def recognize(self, text: str) -> IntentResult:
        if not text or not text.strip():
            return IntentResult(intent=self.INTENT_UNKNOWN, entities={})
        
        # 构建 prompt
        prompt = f"""
请识别用户输入的意图和实体。

用户输入：{text}

意图类型：
- weather_query: 天气查询
- schedule_reminder: 日程提醒
- unknown: 未知意图

实体类型：
- date: 日期，如"今天"、"明天"、"后天"、"12月1日"等
- location: 地点，如"北京"、"上海"、"广州"等
- time: 时间，如"8点"、"下午3点"、"14:30"等
- event: 事件，如"开会"、"吃饭"、"购物"等

请严格按照以下JSON格式返回结果，不要包含任何其他文本：
{{
  "intent": "意图类型",
  "entities": {{
    "date": "日期",
    "location": "地点",
    "time": "时间",
    "event": "事件"
  }}
}}

示例1：
用户输入：北京明天天气怎么样
返回：
{{
  "intent": "weather_query",
  "entities": {{
    "date": "明天",
    "location": "北京",
    "time": "",
    "event": ""
  }}
}}

示例2：
用户输入：提醒我明天下午3点开会
返回：
{{
  "intent": "schedule_reminder",
  "entities": {{
    "date": "明天",
    "location": "",
    "time": "下午3点",
    "event": "开会"
  }}
}}

示例3：
用户输入：你好
返回：
{{
  "intent": "unknown",
  "entities": {{
    "date": "",
    "location": "",
    "time": "",
    "event": ""
  }}
}}
"""
        
        try:
            # 调用大模型
            response = call_llm(prompt)
            print(f"LLM 响应: {response}")
            
            # 检查是否是错误信息
            if response.startswith("错误:"):
                print(f"LLM 调用失败: {response}")
                # Fallback 到规则识别
                return super().recognize(text)
            
            # 解析 JSON 响应
            result = json.loads(response)
            
            # 提取意图和实体
            intent = result.get("intent", self.INTENT_UNKNOWN)
            entities = result.get("entities", {})
            
            # 清理实体，移除空值
            cleaned_entities = {k: v for k, v in entities.items() if v}
            
            return IntentResult(
                intent=intent,
                entities=cleaned_entities,
                confidence=0.95  # 假设大模型的置信度较高
            )
            
        except Exception as e:
            print(f"LLM 意图识别失败: {e}")
            # Fallback 到规则识别
            return super().recognize(text)