from app.rules.registry import load_rules
from app.ai_explainer import generate_ai_explanation
# -------------------------
# Explanation generator
# -------------------------
def generate_explanation(document_type, risk_level, flags):
    if risk_level == "LOW":
        return {
            "summary": "The document is compliant.",
            "rules_triggered": [],
            "reasoning": "No compliance rules were violated.",
            "recommendation": "Document is safe for use."
        }

    return {
        "summary": f"Document classified as {risk_level} risk.",
        "rules_triggered": flags,
        "reasoning": "One or more compliance rules were triggered.",
        "recommendation": "Review document before approval."
    }


# -------------------------
# Pipeline entry point
# -------------------------
async def process_document(event):
    document_id = event["document_id"]
    extracted_text = event.get("extracted_text", "")

    print(f"[PIPELINE] Processing document {document_id}")

    # Step 1: Classification
    document_type = "INFORMATIONAL"

    # Step 2: Rule-based compliance
    compliance_result = evaluate_compliance(extracted_text)

    # Step 3: Explanation
    explanation = generate_ai_explanation(
    document_type=document_type,
    risk_level=compliance_result["risk_level"],
    flags=compliance_result["flags"],
)

    result = {
        "document_id": document_id,
        "document_type": document_type,
        "risk_level": compliance_result["risk_level"],
        "status": compliance_result["status"],
        "flags": compliance_result["flags"],
        "confidence": compliance_result["confidence"],
        "explanation": explanation,
    }

    print(f"[PIPELINE COMPLETED] {document_id}")
    return result


# -------------------------
# Compliance evaluation
# -------------------------
def evaluate_compliance(extracted_text: str):
    rules = load_rules()
    flags = []
    max_severity = "LOW"
    confidence_scores = []

    for rule in rules:
        result = rule.evaluate(extracted_text)
        if result.violated:
            flags.append(rule.id)
            confidence_scores.append(result.confidence)
            if rule.severity == "HIGH":
                max_severity = "HIGH"

    status = "NON_COMPLIANT" if max_severity == "HIGH" else "COMPLIANT"

    return {
        "status": status,
        "risk_level": max_severity,
        "flags": flags,
        "confidence": max(confidence_scores) if confidence_scores else 1.0,
    }