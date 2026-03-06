import re
from app.rules.base import ComplianceRule, RuleResult

class PIIRule(ComplianceRule):
    id = "PII-001"
    severity = "HIGH"

    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_REGEX = r"\b\d{10}\b"
    ID_REGEX = r"\b\d{6,12}\b"   # generic ID / roll no pattern

    def evaluate(self, text: str) -> RuleResult:
        if re.search(self.EMAIL_REGEX, text):
            return RuleResult(True, "Email address detected", 0.9)

        if re.search(self.PHONE_REGEX, text):
            return RuleResult(True, "Phone number detected", 0.85)

        if re.search(self.ID_REGEX, text):
            return RuleResult(True, "Possible ID number detected", 0.7)

        return RuleResult(False)