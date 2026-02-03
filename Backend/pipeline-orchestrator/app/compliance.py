import re

def evaluate_compliance(text: str) -> dict:
    flags = []

    # Rule 1: University name must exist
    if "BHARATI VIDYAPEETH" not in text.upper():
        flags.append("University name not found")

    # Rule 2: Roll number pattern
    if not re.search(r"\b\d{11}\b", text):
        flags.append("Roll number missing or invalid")

    # Determine document type
    document_type = "STUDENT_ID" if "UNIV" in text.upper() else "UNKNOWN"

    # Risk logic
    if len(flags) == 0:
        risk = "LOW"
        confidence = 0.95
    elif len(flags) == 1:
        risk = "MEDIUM"
        confidence = 0.75
    else:
        risk = "HIGH"
        confidence = 0.5

    return {
        "document_type": document_type,
        "risk_level": risk,
        "flags": flags,
        "confidence": confidence
    }