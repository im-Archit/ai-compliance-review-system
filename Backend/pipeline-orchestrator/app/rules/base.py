from abc import ABC, abstractmethod
from typing import Dict

class RuleResult:
    def __init__(self, violated: bool, message: str = "", confidence: float = 0.0):
        self.violated = violated
        self.message = message
        self.confidence = confidence


class ComplianceRule(ABC):
    id: str
    severity: str  # LOW | MEDIUM | HIGH

    @abstractmethod
    def evaluate(self, text: str) -> RuleResult:
        pass