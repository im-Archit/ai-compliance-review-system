from google.cloud import pubsub_v1
import json
import os

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
TOPIC_ID = "document-uploaded"

publisher = pubsub_v1.PublisherClient()
topic_path = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"

def publish_event(event: dict):
    data = json.dumps(event).encode("utf-8")
    future = publisher.publish(topic_path, data)

    # BLOCK until publish is confirmed
    message_id = future.result()

    print(
        f"[PUBSUB] Published message {message_id} "
        f"to topic {topic_path}"
    )