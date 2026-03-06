import json
import os
from google.cloud import pubsub_v1
from google.cloud import storage
from app.vision import extract_text

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
SUBSCRIPTION_ID = "ocr-service-sub"
PIPELINE_TOPIC_PATH = publisher.topic_path(
    PROJECT_ID, "document-pipeline-events"
)


subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    PROJECT_ID, SUBSCRIPTION_ID
)

def callback(message):
    event = None  # ensure scope visibility

    try:
        event = json.loads(message.data.decode("utf-8"))
        print(f"[OCR RECEIVED] {event}")

        storage_path = event.get("metadata", {}).get("storage_path")
        if not storage_path or not storage_path.startswith("gs://"):
            raise ValueError("Invalid or missing GCS storage_path in event")

        # Extract bucket + blob
        _, _, bucket_name, *blob_parts = storage_path.split("/")
        blob_name = "/".join(blob_parts)

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Preserve original file extension
        original_filename = os.path.basename(blob_name)
        _, ext = os.path.splitext(original_filename)

        # Fallback if extension missing
        if not ext:
            content_type = event.get("metadata", {}).get("content_type", "")
            if "pdf" in content_type:
                ext = ".pdf"
            elif "png" in content_type:
                ext = ".png"
            elif "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            else:
                ext = ".bin"

        temp_file_path = f"/tmp/{event['document_id']}{ext}"
        blob.download_to_filename(temp_file_path)

        text = extract_text(temp_file_path)
        print(f"[OCR TEXT EXTRACTED]\n{text[:300]}")

        # Clean up temp file after processing
        try:
            os.remove(temp_file_path)
        except Exception:
            pass

        success_event = {
            "event_type": "OCR_COMPLETED",
            "document_id": event["document_id"],
            "timestamp": event.get("timestamp"),
            "metadata": {
                "ocr_status": "COMPLETED",
                "text_length": len(text)
            },
            "extracted_text": text[:5000]
        }

        publisher.publish(
            PIPELINE_TOPIC_PATH,
            json.dumps(success_event).encode("utf-8")
        )

        print("[OCR SUCCESS EVENT PUBLISHED]")

        message.ack()

    except Exception as e:
        print(f"[OCR ERROR] {e}")

        failure_event = {
            "event_type": "OCR_FAILED",
            "document_id": event.get("document_id") if event else None,
            "timestamp": event.get("timestamp") if event else None,
            "metadata": {
                "stage": "OCR",
                "error": str(e)
            }
        }

        try:
            publisher.publish(
                PIPELINE_TOPIC_PATH,
                json.dumps(failure_event).encode("utf-8")
            )
            print("[OCR FAILURE EVENT PUBLISHED]")
        except Exception as pub_err:
            print(f"[OCR FAILURE PUBLISH ERROR] {pub_err}")

        message.ack()

def start_consumer():
    subscriber.subscribe(subscription_path, callback=callback)
    print("OCR Service listening for document-uploaded events...")