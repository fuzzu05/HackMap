import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ..models.hackathon import HackathonDocument, RecommendationDocument
from ..firebase.client import write_user_recommendations, get_firestore_client
from .engine import RecommendationEngine

logger = logging.getLogger(__name__)


def generate_recommendations_for_user(
    user_id: str,
    user_profile: Dict,
    hackathons: List[HackathonDocument],
    top_n: int = 10,
    dry_run: bool = False,
) -> RecommendationDocument:
    """
    Evaluates hackathons against user_profile, builds a RecommendationDocument,
    and writes it to `/users/{user_id}/recommendations/latest` in Firestore.
    """
    logger.info("Generating recommendations for user %s (dry_run=%s)", user_id, dry_run)
    engine = RecommendationEngine(default_top_n=top_n)
    ranked_list = engine.fit_and_score_hackathons(
        user_profile=user_profile,
        hackathons=hackathons,
        top_n=top_n,
    )

    rec_doc = RecommendationDocument(
        updatedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        algorithmVersion="v1.0-hybrid-content",
        rankedHackathons=ranked_list,
    )

    if not dry_run:
        try:
            db_client = get_firestore_client()
            write_user_recommendations(user_id=user_id, rec_doc=rec_doc, db=db_client)
        except Exception as e:
            logger.warning(
                "Firestore unreachable (%s). Simulated in-memory recommendation generation.",
                str(e),
            )
    else:
        logger.info("Dry-run enabled: skipped Firestore upsert for user %s", user_id)

    return rec_doc
