import json
import os
from google.cloud import pubsub_v1
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db import SessionLocal
from app.models import ComplianceDecision, AuditLog, ProcessingStage

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
SUBSCRIPTION_ID = "compliance-store-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    PROJECT_ID, SUBSCRIPTION_ID
)
print(f"[COMPLIANCE STORE] Listening to subscription: {subscription_path}")

def callback(message):
    try:
        event = json.loads(message.data.decode("utf-8"))
        print(f"[EVENT RECEIVED] {event}")

        db: Session = SessionLocal()
        try:
            event_type = event.get("event_type")
            document_id = event.get("document_id")

            if not document_id:
                print("[WARNING] Missing document_id. Skipping event.")
                message.ack()
                return

            # ============================================================
            # 1️⃣ HANDLE NON-COMPLIANCE PIPELINE EVENTS
            # ============================================================
            if event_type and event_type != "COMPLIANCE_RESULT":
                print(f"[PIPELINE STAGE] {event_type}")

                audit = AuditLog(
                    document_id=document_id,
                    event=event_type,
                    details=event.get("metadata", {}),
                )

                db.add(audit)
                db.commit()

                message.ack()
                return

            # ============================================================
            # 2️⃣ HANDLE COMPLIANCE RESULT EVENT
            # ============================================================
            print("[PROCESSING COMPLIANCE RESULT]")

            existing = (
                db.query(ComplianceDecision)
                .filter(ComplianceDecision.document_id == document_id)
                .first()
            )

            if existing:
                print("[INFO] Updating existing decision")

                existing.document_type = event["document_type"]
                existing.risk_level = event["risk_level"]
                existing.status = event["status"]
                existing.flags = event.get("flags", [])
                existing.confidence = event.get("confidence")
                existing.explanation = event.get("explanation")
                existing.evaluated_at = datetime.utcnow()
                existing.processing_stage = ProcessingStage.STORED

                audit = AuditLog(
                    document_id=document_id,
                    event="COMPLIANCE_UPDATED",
                    details={
                        "status": event["status"],
                        "risk_level": event["risk_level"],
                    },
                )
                db.add(audit)

            else:
                print("[INFO] Creating new decision")

                decision = ComplianceDecision(
                    document_id=document_id,
                    document_type=event["document_type"],
                    risk_level=event["risk_level"],
                    status=event["status"],
                    flags=event.get("flags", []),
                    confidence=event.get("confidence"),
                    explanation=event.get("explanation"),
                    evaluated_at=datetime.utcnow(),
                    processing_stage=ProcessingStage.STORED,
                )

                db.add(decision)

                audit = AuditLog(
                    document_id=document_id,
                    event="COMPLIANCE_STORED",
                    details={
                        "status": event["status"],
                        "risk_level": event["risk_level"],
                    },
                )
                db.add(audit)

            db.commit()

            print("[COMPLIANCE STORED]")
            message.ack()
        finally:
            db.close()

    except Exception as e:
        print(f"[STORE ERROR] {e}")
        message.nack()

def start_consumer():
    streaming_future = subscriber.subscribe(subscription_path, callback=callback)
    print("Compliance Store Service listening...")

    def _callback_done(future):
        try:
            future.result()
        except Exception as e:
            print(f"[SUBSCRIBER ERROR] {e}")

    streaming_future.add_done_callback(_callback_done)