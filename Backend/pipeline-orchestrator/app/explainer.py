import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def generate_ai_explanation(document_type, risk_level, flags):
    """
    Generates a short AI explanation.
    Falls back safely if OpenAI is unavailable.
    """

    # Hard fallback (always works)
    fallback = (
        "The document is compliant. No high-risk or restricted content "
        "was detected based on the configured compliance rules."
    )

    # If OpenAI SDK or key is missing → fallback
    api_key = os.getenv("OPENAI_API_KEY")
    if not OpenAI or not api_key:
        return fallback

    try:
        client = OpenAI(api_key=api_key)

        prompt = (
            f"Explain in one short sentence why this document is {risk_level.lower()} risk. "
            f"Document type: {document_type}. "
            f"Triggered rules: {flags if flags else 'none'}."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",   # cheap + fast
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=40,         # VERY IMPORTANT (cost control)
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception:
        # Absolute safety fallback
        return fallback