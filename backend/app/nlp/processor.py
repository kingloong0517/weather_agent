from typing import Dict, Optional
from .intent_recognizer import IntentRecognizer, IntentResult
from .llm_intent_recognizer import LLMIntentRecognizer
from .entity_extractor import EntityExtractor


class NLUProcessor:
    def __init__(self, default_city: str = "北京", use_llm: bool = True):
        self.intent_recognizer = LLMIntentRecognizer() if use_llm else IntentRecognizer()
        self.entity_extractor = EntityExtractor(default_city=default_city)

    def process(self, text: str) -> Dict:
        intent_result = self.intent_recognizer.recognize(text)

        entities = {}
        if intent_result.intent != IntentRecognizer.INTENT_UNKNOWN:
            # 如果大模型已经提取了实体，就使用大模型的结果
            if hasattr(self.intent_recognizer, 'entities') and self.intent_recognizer.entities:
                entities = self.intent_recognizer.entities
            else:
                entities = self.entity_extractor.extract_all(text)
        else:
            entities = self.entity_extractor.extract_all(text)

        return {
            "intent": intent_result.intent,
            "entities": entities,
            "confidence": intent_result.confidence
        }

    def set_default_city(self, city: str) -> None:
        self.entity_extractor.default_city = city
