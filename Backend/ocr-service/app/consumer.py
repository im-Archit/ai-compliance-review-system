import json
import os
from google.cloud import pubsub_v1
from app.vision import extract_text

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
SUBSCRIPTION_ID = "ocr-service-sub"
OCR_TOPIC_PATH = publisher.topic_path(PROJECT_ID, "document-ocr-completed")

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    PROJECT_ID, SUBSCRIPTION_ID
)

def callback(message):
    try:
        event = json.loads(message.data.decode("utf-8"))
        print(f"[OCR RECEIVED] {event}")

        storage_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "upload-service",
            event["storage_path"]
        )

        text = extract_text(storage_path)
        print(f"[OCR TEXT EXTRACTED]\n{text[:300]}")

        event_out = {
            "document_id": event["document_id"],
            "ocr_status": "COMPLETED",
            "extracted_text": text[:5000]  # cap size for Pub/Sub
        }

        publisher.publish(
            OCR_TOPIC_PATH,
            json.dumps(event_out).encode("utf-8")
        )

        print("[OCR EVENT PUBLISHED] document-ocr-completed")

        message.ack()

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        message.ack()  # ack anyway to avoid infinite retry

def start_consumer():
    subscriber.subscribe(subscription_path, callback=callback)
    print("OCR Service listening for document-uploaded events...")