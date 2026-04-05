from typing import Dict, Optional
from .intent_recognizer import IntentRecognizer, IntentResult
from .entity_extractor import EntityExtractor


class NLUProcessor:
    def __init__(self, default_city: str = "北京"):
        self.intent_recognizer = IntentRecognizer()
        self.entity_extractor = EntityExtractor(default_city=default_city)

    def process(self, text: str) -> Dict:
        intent_result = self.intent_recognizer.recognize(text)

        entities = {}
        if intent_result.intent != IntentRecognizer.INTENT_UNKNOWN:
            entities = self.entity_extractor.extract_all(text)

        return {
            "intent": intent_result.intent,
            "entities": entities,
            "confidence": intent_result.confidence
        }

    def set_default_city(self, city: str) -> None:
        self.entity_extractor.default_city = city
