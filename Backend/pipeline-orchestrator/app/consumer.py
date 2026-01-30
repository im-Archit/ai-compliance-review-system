from google.cloud import pubsub_v1
import asyncio
import json
import os
import threading
from app.pipeline import process_document

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = "pipeline-orchestrator-sub"

def start_consumer():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        PROJECT_ID, SUBSCRIPTION_ID
    )

    def callback(message):
        event = json.loads(message.data.decode("utf-8"))
        print(f"[EVENT RECEIVED] {event}")
        # Run async pipeline correctly
        asyncio.run(process_document(event))
        message.ack()

    print("Pipeline Orchestrator listening for Pub/Sub events...")

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )

    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
