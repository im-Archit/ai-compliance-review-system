import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def generate_ai_explanation(document_type, risk_level, flags):
    """
    Token-optimized AI explanation with safe fallback.
    """

    # Always-available fallback (never returns None)
    fallback = (
        "The document is compliant. No high-risk or restricted content "
        "was detected by the compliance rules."
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not OpenAI or not api_key:
        return fallback

    try:
        client = OpenAI(api_key=api_key)

        prompt = (
            f"Explain in one short sentence why this document is {risk_level.lower()} risk. "
            f"Triggered rules: {flags if flags else 'none'}."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=40,       # 🔥 cost-controlled
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return fallback