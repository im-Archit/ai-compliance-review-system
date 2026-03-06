# from app.rules.pii_rule import PIIRule
# from app.rules.financial_rule import FinancialDataRule
# from app.rules.health_rule import HealthDataRule

# def load_rules():
#     """
#     Central registry for all compliance rules.

#     Each rule must implement:
#     - id
#     - severity ("LOW" | "HIGH")
#     - evaluate(text) -> RuleResult
#     """
#     return [
#         PIIRule(),
#         FinancialDataRule(),
#         HealthDataRule(),
#     ]

from app.rules.healthcare_rule import HealthcareRule

def load_rules():
    return [
        HealthcareRule(),
    ]