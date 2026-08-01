import os
import logging
from typing import Optional
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from algoliasearch.search_client import SearchClient
from ../models.hackathon import HackathonDocument, RecommendationDocument

load_dotenv()

# Initialize Algolia
try:
    algolia_app_id = os.getenv("ALGOLIA_APP_ID")
    algolia_admin_key = os.getenv("ALGOLIA_ADMIN_KEY")
    if algolia_app_id and algolia_admin_key:
        search_client = SearchClient.create(algolia_app_id, algolia_admin_key)
        algolia_index = search_client.init_index("hackathons")
    else:
        algolia_index = None
except Exception as e:
    algolia_index = None

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
    Upserts a normalized HackathonDocument into the `/hackathons` collection and Algolia.
    Returns the document ID.
    """
    client = db or get_firestore_client()
    doc_data = hackathon_doc.model_dump()
    
    # Firestore sync
    doc_ref = client.collection("hackathons").document(hackathon_doc.id)
    doc_ref.set(doc_data, merge=True)
    logger.info("Upserted hackathon document /hackathons/%s", hackathon_doc.id)
    
    # Algolia sync
    if algolia_index:
        try:
            algolia_doc = doc_data.copy()
            algolia_doc["objectID"] = hackathon_doc.id
            algolia_index.save_object(algolia_doc)
            logger.info("Pushed hackathon %s to Algolia index", hackathon_doc.id)
        except Exception as e:
            logger.error("Failed to push hackathon %s to Algolia: %s", hackathon_doc.id, str(e))

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
