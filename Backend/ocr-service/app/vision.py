import pytesseract
from PIL import Image


def extract_text_and_confidence(file_path: str) -> dict:
    image = Image.open(file_path)

    text = pytesseract.image_to_string(image).strip()

    data = pytesseract.image_to_data(
        image, output_type=pytesseract.Output.DICT
    )

    confidences = []
    for conf in data.get("conf", []):
        try:
            conf_val = int(conf)
            if conf_val > 0:
                confidences.append(conf_val)
        except ValueError:
            continue

    avg_confidence = (
        sum(confidences) / len(confidences)
        if confidences else 50
    )

    return {
        "text": text,
        "confidence": round(avg_confidence / 100, 2)
    }


# ✅ REQUIRED for consumer.py compatibility
def extract_text(file_path: str) -> str:
    return extract_text_and_confidence(file_path)["text"]