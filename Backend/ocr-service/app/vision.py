from google.cloud import vision

client = vision.ImageAnnotatorClient()

def extract_text(file_path: str) -> str:
    with open(file_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(response.error.message)

    texts = response.text_annotations
    return texts[0].description if texts else ""