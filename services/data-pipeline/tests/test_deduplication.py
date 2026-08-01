import pytest
from src.models.hackathon import (
    HackathonDocument,
    HackathonMode,
    HackathonStatus,
    Organizer,
    Location,
    Dates,
    Prizes,
)
from src.deduplication.engine import (
    compute_title_similarity,
    merge_hackathon_records,
    DeduplicationEngine,
)
from src.normalization.normalizer import generate_dedup_hash


def _create_sample_doc(slug: str, source: str, title: str, start_date: str, prize: float, tags: list[str]) -> HackathonDocument:
    h = generate_dedup_hash(title, start_date)
    return HackathonDocument(
        id=slug,
        source=source,
        sourceUrl=f"https://{source.lower()}.com/events/{slug}",
        title=title,
        tagline="Sample event",
        description=f"Description for {title}",
        organizer=Organizer(name=source, url=f"https://{source.lower()}.com"),
        mode=HackathonMode.ONLINE,
        location=Location(city="San Francisco", country="USA", isOnline=True),
        dates=Dates(
            registrationOpen="2026-08-01T00:00:00Z",
            registrationClose="2026-09-01T00:00:00Z",
            hackathonStart=start_date,
            hackathonEnd="2026-09-15T00:00:00Z",
        ),
        prizes=Prizes(totalPoolUsd=prize, currency="USD"),
        tags=tags,
        techStack=["Python", "React"],
        dedupHash=h,
        status=HackathonStatus.UPCOMING,
        lastScrapedAt="2026-08-01T12:00:00Z",
    )


def test_compute_title_similarity():
    sim = compute_title_similarity("Global AI Hackathon 2026", "Global AI Hackathon '26")
    assert sim >= 0.85
    sim_diff = compute_title_similarity("Global AI Hackathon 2026", "Web3 DeFi Challenge 2026")
    assert sim_diff < 0.50


def test_merge_hackathon_records():
    doc_mlh = _create_sample_doc(
        "mlh-1", "MLH", "Global AI Agents Hackathon 2026", "2026-09-12T00:00:00Z", 50000.0, ["AI", "MLH"]
    )
    doc_devpost = _create_sample_doc(
        "devpost-1", "Devpost", "Global AI Agents Hackathon 2026", "2026-09-12T00:00:00Z", 75000.0, ["AI", "Agents", "LangChain"]
    )

    merged = merge_hackathon_records(doc_mlh, doc_devpost)
    assert merged.prizes.totalPoolUsd == 75000.0
    assert "MLH+Devpost" in merged.source or "Devpost" in merged.source
    assert set(["AI", "MLH", "Agents", "LangChain"]).issubset(set(merged.tags))


def test_deduplication_engine():
    engine = DeduplicationEngine(similarity_threshold=0.85, date_window_days=3)
    doc1 = _create_sample_doc(
        "mlh-1", "MLH", "Global AI Agents Hackathon 2026", "2026-09-12T00:00:00Z", 50000.0, ["AI", "MLH"]
    )
    doc2 = _create_sample_doc(
        "devpost-1", "Devpost", "Global AI Agents Hackathon '26", "2026-09-12T00:00:00Z", 75000.0, ["AI", "Agents"]
    )

    _, is_dup1 = engine.process_record(doc1)
    assert not is_dup1  # first record is unique

    merged, is_dup2 = engine.process_record(doc2)
    assert is_dup2  # second record is detected as duplicate and merged!
    assert len(engine.get_deduplicated_records()) == 1
    assert merged.prizes.totalPoolUsd == 75000.0
