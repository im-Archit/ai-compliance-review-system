import os
import json
import threading
import asyncio
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = "orchestrator-ocr-sub"
PIPELINE_EVENTS_TOPIC = "document-pipeline-events"
COMPLIANCE_TOPIC = "document-compliance-evaluated"
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

            event_type = event.get("event_type")

            # Only process OCR_COMPLETED events
            if event_type != "OCR_COMPLETED":
                print(f"[PIPELINE] Ignoring event type: {event_type}")
                message.ack()
                return

            document_id = event.get("document_id")
            extracted_text = event.get("extracted_text")

            if not extracted_text:
                print("[PIPELINE] No OCR text found, skipping.")
                message.ack()
                return

            from app.pipeline import process_document

            # Run pipeline processing
            result = asyncio.run(process_document({
                "document_id": document_id,
                "extracted_text": extracted_text
            }))

            # ------------------------------------------------------------
            # 1️⃣ Publish ANALYSIS_COMPLETED stage event
            # ------------------------------------------------------------
            publish_event(
                PIPELINE_EVENTS_TOPIC,
                {
                    "event_type": "ANALYSIS_COMPLETED",
                    "document_id": document_id,
                    "timestamp": event.get("timestamp"),
                    "metadata": {
                        "summary": "Document analysis completed"
                    }
                }
            )

            # ------------------------------------------------------------
            # 2️⃣ Publish COMPLIANCE_RESULT event
            # ------------------------------------------------------------
            compliance_event = {
                "event_type": "COMPLIANCE_RESULT",
                "document_id": result.get("document_id"),
                "document_type": result.get("document_type"),
                "risk_level": result.get("risk_level"),
                "status": result.get("status"),
                "flags": result.get("flags", []),
                "confidence": result.get("confidence"),
                "explanation": result.get("explanation"),
                "timestamp": event.get("timestamp"),
            }

            publish_event(
                COMPLIANCE_TOPIC,
                compliance_event
            )

            print("[COMPLIANCE RESULT EVENT PUBLISHED]", compliance_event)
            message.ack()

        except Exception as e:
            print("[PIPELINE ERROR]", e)

            try:
                failure_event = {
                    "event_type": "ANALYSIS_FAILED",
                    "document_id": event.get("document_id") if "event" in locals() else None,
                    "timestamp": event.get("timestamp") if "event" in locals() else None,
                    "metadata": {
                        "stage": "ANALYSIS",
                        "error": str(e)
                    }
                }

                publish_event(
                    PIPELINE_EVENTS_TOPIC,
                    failure_event
                )

                print("[ANALYSIS FAILURE EVENT PUBLISHED]", failure_event)

            except Exception as publish_error:
                print("[FAILURE EVENT PUBLISH ERROR]", publish_error)

            # Ack to prevent infinite retry loop
            message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )

    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
