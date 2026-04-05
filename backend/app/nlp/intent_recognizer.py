from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class IntentResult:
    intent: str
    entities: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict:
        return {
            "intent": self.intent,
            "entities": self.entities,
            "confidence": self.confidence
        }


class IntentRecognizer:
    INTENT_WEATHER = "weather_query"
    INTENT_REMINDER = "schedule_reminder"
    INTENT_UNKNOWN = "unknown"

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        INTENT_WEATHER: ["天气", "下雨", "伞", "穿衣", "穿", "衣服", "气温", "温度", "冷", "热", "晴天", "阴天", "雨", "雪", "风", "出太阳"],
        INTENT_REMINDER: ["提醒", "日程", "会议", "备忘", "记", "通知", "安排"]
    }

    def __init__(self):
        pass

    def recognize(self, text: str) -> IntentResult:
        if not text or not text.strip():
            return IntentResult(intent=self.INTENT_UNKNOWN, entities={})

        text = text.strip()
        matched_intent = self.INTENT_UNKNOWN
        max_score = 0

        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > max_score:
                max_score = score
                matched_intent = intent

        confidence = min(max_score / 3.0, 1.0) if max_score > 0 else 0.0

        return IntentResult(
            intent=matched_intent,
            entities={},
            confidence=confidence
        )
