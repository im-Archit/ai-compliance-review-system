
"""
AI Explanation Module (Rule-Based, No External APIs)

Purpose:
- Generate a human-readable explanation of compliance decisions
- DOES NOT decide compliance
- Uses rule evaluation outputs only
"""

from typing import List


def generate_ai_summary(
    document_type: str,
    risk_level: str,
    status: str,
    flags: List[str],
    confidence: float,
) -> str:
    """
    Generate a natural language explanation for a compliance decision.

    This function is intentionally deterministic and does NOT call
    any external AI or LLM APIs. It is safe for audits and offline use.
    """

    base_summary = (
        f"The document was classified as {document_type} and "
        f"evaluated as {status} with a {risk_level} risk level."
    )

    if not flags:
        rule_summary = (
            " No compliance rules were violated during the evaluation."
        )
    else:
        rule_summary = (
            " The following compliance rules were triggered: "
            + ", ".join(flags)
            + "."
        )

    confidence_summary = (
        f" The confidence score for this evaluation is {confidence:.2f}."
    )

    return base_summary + rule_summary + confidence_summary