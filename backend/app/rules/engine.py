from typing import Any, Callable, Dict, List


class Rule:
    def __init__(
        self,
        name: str,
        condition: Callable[[str], bool],
        action: Callable[[str], Any]
    ):
        self.name = name
        self.condition = condition
        self.action = action


class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> None:
        self.rules = [r for r in self.rules if r.name != rule_name]

    def execute(self, query: str) -> Dict[str, Any]:
        for rule in self.rules:
            if rule.condition(query):
                return {
                    "matched_rule": rule.name,
                    "result": rule.action(query)
                }
        return {
            "matched_rule": None,
            "result": None
        }
