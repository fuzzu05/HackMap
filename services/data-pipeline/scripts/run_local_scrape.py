import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure src package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.hackathon import (
    HackathonDocument,
    HackathonMode,
    HackathonStatus,
    Organizer,
    Location,
    Dates,
    Prizes,
)
from src.normalization.normalizer import generate_dedup_hash, normalize_date_to_utc
from src.deduplication.engine import DeduplicationEngine
from src.crawler.spiders.devpost_spider import DevpostSpider
from src.crawler.spiders.mlh_spider import MLHSpider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_local_scrape")


def generate_large_curated_dataset() -> list[dict]:
    """
    Generates 100+ realistic, diverse hackathon records across Devpost, MLH, Luma, and Unstop,
    including intentional cross-listed duplicates to demonstrate deduplication and merging.
    """
    items = []
    base_date = datetime.now(timezone.utc)

    domains_and_sources = [
        ("Devpost", "https://devpost.com/hackathons/"),
        ("MLH", "https://mlh.io/events/"),
        ("Luma", "https://lu.ma/"),
        ("Unstop", "https://unstop.com/hackathons/"),
    ]

    themes = [
        ("AI Agents & LLM Revolution", ["AI / Machine Learning", "LLM", "Autonomous Agents"], ["Python", "LangChain", "Next.js", "OpenAI"]),
        ("Web3 DeFi & Smart Contracts", ["Web3", "Blockchain", "DeFi"], ["Solidity", "Rust", "Ethereum", "React"]),
        ("ClimateTech Carbon Neutral", ["ClimateTech", "Sustainability", "Clean Energy"], ["Python", "TensorFlow", "IoT", "AWS"]),
        ("FinTech NextGen Payments", ["FinTech", "Banking", "Payments"], ["Java", "Go", "React Native", "Stripe"]),
        ("CyberSecurity Defense", ["CyberSecurity", "Zero Trust", "DevSecOps"], ["Python", "C++", "Docker", "Linux"]),
        ("MedTech Healthcare AI", ["MedTech", "BioTech", "Digital Health"], ["Python", "PyTorch", "FHIR", "GCP"]),
        ("EdTech Interactive Learning", ["EdTech", "Gamification", "AI Assistant"], ["TypeScript", "Next.js", "Tailwind", "OpenAI"]),
        ("Quantum Computing Frontier", ["Quantum", "Physics", "Algorithms"], ["Qiskit", "Python", "C++", "IBM Quantum"]),
        ("Open Source Hacktober", ["Open Source", "Community", "Developer Tools"], ["TypeScript", "Rust", "Go", "Python"]),
        ("Mobile App UX Innovation", ["Mobile", "Flutter", "React Native"], ["Flutter", "Dart", "Firebase", "Swift"]),
    ]

    modes = [HackathonMode.ONLINE, HackathonMode.HYBRID, HackathonMode.IN_PERSON]
    cities = [("San Francisco", "USA"), ("London", "UK"), ("Berlin", "Germany"), ("Bangalore", "India"), ("Tokyo", "Japan")]

    count = 1
    for i in range(1, 11):
        for theme_name, tags, tech_stack in themes:
            source_name, base_url = domains_and_sources[(count - 1) % len(domains_and_sources)]
            mode = modes[(count - 1) % len(modes)]
            city, country = cities[(count - 1) % len(cities)]
            start_dt = base_date + timedelta(days=count * 3)
            end_dt = start_dt + timedelta(days=2)
            reg_open_dt = start_dt - timedelta(days=30)
            reg_close_dt = start_dt - timedelta(days=2)

            title = f"{theme_name} Hackathon #{i}"
            slug = f"{source_name.lower()}-{count}"
            url = f"{base_url}{theme_name.lower().replace(' ', '-')}-{i}"

            start_utc = normalize_date_to_utc(start_dt.isoformat())
            dedup_hash = generate_dedup_hash(title, start_utc)

            doc = HackathonDocument(
                id=slug,
                source=source_name,
                sourceUrl=url,
                title=title,
                tagline=f"Innovate and compete in {theme_name}",
                description=f"Join developers worldwide for {theme_name} #{i} organized by {source_name} community.",
                organizer=Organizer(name=f"{source_name} Official", url=base_url),
                mode=mode,
                location=Location(city=city if mode != HackathonMode.ONLINE else None, country=country if mode != HackathonMode.ONLINE else None, isOnline=mode != HackathonMode.IN_PERSON),
                dates=Dates(
                    registrationOpen=normalize_date_to_utc(reg_open_dt.isoformat()),
                    registrationClose=normalize_date_to_utc(reg_close_dt.isoformat()),
                    hackathonStart=start_utc,
                    hackathonEnd=normalize_date_to_utc(end_dt.isoformat()),
                ),
                prizes=Prizes(totalPoolUsd=10000.0 * i, currency="USD"),
                tags=tags,
                techStack=tech_stack,
                eligibility="Global, Open to developers and students",
                dedupHash=dedup_hash,
                status=HackathonStatus.UPCOMING,
                lastScrapedAt=normalize_date_to_utc(base_date.isoformat()),
            )
            items.append(doc.model_dump())
            count += 1

    # Add intentional cross-listed duplicates between MLH and Devpost to verify merging
    devpost_spider = DevpostSpider(use_mock_seeds=True)
    mlh_spider = MLHSpider(use_mock_seeds=True)
    for item in devpost_spider._generate_mock_seeds():
        items.append(item)
    for item in mlh_spider._generate_mock_seeds():
        items.append(item)

    return items


def run_scrape_and_dedup():
    """
    Runs local data collection across spiders and synthetic dataset,
    executes DeduplicationEngine, validates all output records,
    and writes 100+ clean deduplicated hackathon records to output/hackathons_dump.json.
    """
    logger.info("Starting Phase 2 Local Scrape & Deduplication pipeline...")

    engine = DeduplicationEngine(similarity_threshold=0.85, date_window_days=3)
    raw_items = generate_large_curated_dataset()
    logger.info("Collected %d raw hackathon records from spiders and multi-platform seeds.", len(raw_items))

    duplicates_count = 0
    for raw_item in raw_items:
        doc = HackathonDocument.model_validate(raw_item)
        merged_doc, is_duplicate = engine.process_record(doc)
        if is_duplicate:
            duplicates_count += 1

    unique_records = engine.get_deduplicated_records()
    logger.info("Deduplication completed! Merged %d duplicate records.", duplicates_count)
    logger.info("Total unique deduplicated hackathons ready for database ingestion: %d", len(unique_records))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "hackathons_dump.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([doc.model_dump() for doc in unique_records], f, indent=2)

    logger.info("Saved %d deduplicated hackathons to %s", len(unique_records), out_path)
    return unique_records


if __name__ == "__main__":
    run_scrape_and_dedup()
