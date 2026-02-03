import os
import json
import threading
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = "orchestrator-ocr-sub"
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

def publish_event(topic, data):
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, data=json.dumps(data).encode("utf-8"))
    return future.result()


# Consumer function for Pub/Sub events
def start_consumer():
    subscription_path = subscriber.subscription_path(
        PROJECT_ID, SUBSCRIPTION_ID
    )

    def callback(message):
        try:
            event = json.loads(message.data.decode("utf-8"))
            print("[EVENT RECEIVED]", event)

            document_id = event.get("document_id")
            extracted_text = event.get("extracted_text")

            if not extracted_text:
                print("[PIPELINE] No OCR text found, skipping.")
                message.ack()
                return

            # ---- pipeline steps (already existing logic assumed here) ----
            result = {
                "document_id": document_id,
                "document_type": "INFORMATIONAL",
                "risk_level": "LOW",
                "status": "COMPLIANT"
            }

            publish_event(
                "document-compliance-evaluated",
                result
            )

            print("[COMPLIANCE EVENT PUBLISHED]", result)
            message.ack()

        except Exception as e:
            print("[PIPELINE ERROR]", e)
            message.nack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )

    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
