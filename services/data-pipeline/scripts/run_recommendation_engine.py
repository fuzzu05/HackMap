import json
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.recommendation.service import generate_recommendations_for_user
from scripts.run_local_scrape import run_scrape_and_dedup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_recommendation_engine")


def main():
    """
    Runs the recommendation engine against the deduplicated hackathon dataset
    for 3 diverse sample user profiles, writing the results to output/sample_recommendations.json.
    """
    logger.info("Running Phase 4 Recommendation Engine simulation...")
    hackathons = run_scrape_and_dedup()

    sample_profiles = {
        "user_ai_python_01": {
            "preferredTags": ["AI / Machine Learning", "Autonomous Agents", "LLM"],
            "preferredTechStack": ["Python", "LangChain", "OpenAI", "Next.js"],
            "preferredMode": "HYBRID",
        },
        "user_web3_rust_02": {
            "preferredTags": ["Web3", "Blockchain", "DeFi"],
            "preferredTechStack": ["Solidity", "Rust", "Ethereum", "React"],
            "preferredMode": "ONLINE",
        },
        "user_mobile_flutter_03": {
            "preferredTags": ["Mobile", "Flutter", "React Native"],
            "preferredTechStack": ["Flutter", "Dart", "Firebase", "Swift"],
            "preferredMode": "IN_PERSON",
        },
    }

    use_dry_run = not bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CONFIG"))
    results = {}

    for user_id, profile in sample_profiles.items():
        rec_doc = generate_recommendations_for_user(
            user_id=user_id,
            user_profile=profile,
            hackathons=hackathons,
            top_n=5,
            dry_run=use_dry_run,
        )
        results[user_id] = rec_doc.model_dump()
        logger.info(
            "User %s top recommendation: %s (score: %.2f)",
            user_id,
            rec_doc.rankedHackathons[0].hackathonId if rec_doc.rankedHackathons else "None",
            rec_doc.rankedHackathons[0].score if rec_doc.rankedHackathons else 0.0,
        )

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_recommendations.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Saved recommendations for %d test profiles to %s", len(results), out_path)
    return results


if __name__ == "__main__":
    main()
