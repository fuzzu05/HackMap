import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from ..models.hackathon import HackathonDocument, RecommendationDocument

logger = logging.getLogger(__name__)

_db_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """
    Returns a singleton Firestore client instance initialized via Firebase Admin SDK.
    Uses default application credentials or FIREBASE_CONFIG / GOOGLE_APPLICATION_CREDENTIALS environment variables.
    """
    global _db_client
    if _db_client is not None:
        return _db_client

    try:
        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Initialize default app (supports ADC in cloud environments or mock testing)
                firebase_admin.initialize_app()
        _db_client = firestore.client()
        logger.info("Firebase Admin Firestore client initialized successfully.")
        return _db_client
    except Exception as e:
        logger.error("Failed to initialize Firebase Admin Firestore client: %s", str(e))
        raise


def upsert_hackathon(hackathon_doc: HackathonDocument, db: Optional[firestore.Client] = None) -> str:
    """
    Upserts a normalized HackathonDocument into the `/hackathons` collection.
    Returns the document ID.
    """
    client = db or get_firestore_client()
    doc_ref = client.collection("hackathons").document(hackathon_doc.id)
    doc_ref.set(hackathon_doc.model_dump(), merge=True)
    logger.info("Upserted hackathon document /hackathons/%s", hackathon_doc.id)
    return hackathon_doc.id


def write_user_recommendations(
    user_id: str,
    rec_doc: RecommendationDocument,
    db: Optional[firestore.Client] = None,
    doc_id: str = "latest",
) -> str:
    """
    Writes a RecommendationDocument into the `/users/{user_id}/recommendations` subcollection
    for direct read consumption by Zubaida's REST APIs.
    """
    client = db or get_firestore_client()
    doc_ref = (
        client.collection("users")
        .document(user_id)
        .collection("recommendations")
        .document(doc_id)
    )
    doc_ref.set(rec_doc.model_dump(), merge=True)
    logger.info("Wrote recommendations to /users/%s/recommendations/%s", user_id, doc_id)
    return doc_id
