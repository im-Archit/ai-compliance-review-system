import json
import os
from google.cloud import pubsub_v1
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db import SessionLocal
from app.models import ComplianceDecision

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
SUBSCRIPTION_ID = "compliance-store-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    PROJECT_ID, SUBSCRIPTION_ID
)

def callback(message):
    try:
        event = json.loads(message.data.decode("utf-8"))
        print(f"[COMPLIANCE RECEIVED] {event}")

        db: Session = SessionLocal()

        decision = ComplianceDecision(
            document_id=event["document_id"],
            status=event["status"],
            risk_level=event["risk_level"],
            document_type=event["document_type"],
            flags=event.get("flags", []),
        )

        db.add(decision)
        db.commit()
        db.close()

        print("[COMPLIANCE STORED]")
        message.ack()

    except Exception as e:
        print(f"[STORE ERROR] {e}")
        message.ack()  # prevent infinite retry

def start_consumer():
    subscriber.subscribe(subscription_path, callback=callback)
    print("Compliance Store Service listening...")