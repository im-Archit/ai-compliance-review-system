# Backend/pipeline-orchestrator/app/rules/healthcare_rule.py

class RuleResult:
    def __init__(self, violated: bool, confidence: float = 1.0):
        self.violated = violated
        self.confidence = confidence


class HealthcareRule:
    id = "HEALTHCARE_001"
    severity = "LOW"

    def evaluate(self, text: str) -> RuleResult:
        keywords = [
            "diagnose",
            "treat",
            "cure",
            "medical advice",
            "prescription",
        ]

        lowered = text.lower()

        for kw in keywords:
            if kw in lowered:
                return RuleResult(violated=True, confidence=0.7)

        return RuleResult(violated=False, confidence=1.0)