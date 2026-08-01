import pytest
from datetime import datetime, timezone, timedelta
from src.models.hackathon import (
    HackathonDocument,
    HackathonMode,
    HackathonStatus,
    Organizer,
    Location,
    Dates,
    Prizes,
)
from src.recommendation.engine import (
    RecommendationEngine,
    score_hackathon_for_user,
    _tokenize_profile,
)
from src.normalization.normalizer import generate_dedup_hash, normalize_date_to_utc


def _make_hackathon(slug: str, title: str, tags: list[str], tech_stack: list[str], mode: HackathonMode, days_to_close: int = 20) -> HackathonDocument:
    now = datetime.now(timezone.utc)
    reg_close = now + timedelta(days=days_to_close)
    start_date = reg_close + timedelta(days=5)
    end_date = start_date + timedelta(days=2)

    return HackathonDocument(
        id=slug,
        source="TestPlatform",
        sourceUrl=f"https://test.com/{slug}",
        title=title,
        tagline="Test Event",
        description="Detailed description for testing",
        organizer=Organizer(name="Test Org", url="https://test.com"),
        mode=mode,
        location=Location(city="San Francisco", country="USA", isOnline=True),
        dates=Dates(
            registrationOpen=normalize_date_to_utc(now.isoformat()),
            registrationClose=normalize_date_to_utc(reg_close.isoformat()),
            hackathonStart=normalize_date_to_utc(start_date.isoformat()),
            hackathonEnd=normalize_date_to_utc(end_date.isoformat()),
        ),
        prizes=Prizes(totalPoolUsd=50000.0, currency="USD"),
        tags=tags,
        techStack=tech_stack,
        dedupHash=generate_dedup_hash(title, normalize_date_to_utc(start_date.isoformat())),
        status=HackathonStatus.UPCOMING,
        lastScrapedAt=normalize_date_to_utc(now.isoformat()),
    )


def test_score_hackathon_matches_profile_higher():
    profile = {
        "preferredTags": ["AI / Machine Learning", "LLM"],
        "preferredTechStack": ["Python", "LangChain"],
        "preferredMode": "HYBRID",
    }
    tokens = _tokenize_profile(profile)
    now = datetime.now(timezone.utc)

    ai_hack = _make_hackathon("ai-1", "Global AI Hackathon", ["AI / Machine Learning"], ["Python", "LangChain"], HackathonMode.HYBRID)
    web3_hack = _make_hackathon("web3-1", "Web3 DeFi Hack", ["Web3", "Blockchain"], ["Solidity", "Rust"], HackathonMode.ONLINE)

    score_ai, reasons_ai = score_hackathon_for_user(tokens, profile, ai_hack, now)
    score_web3, reasons_web3 = score_hackathon_for_user(tokens, profile, web3_hack, now)

    assert score_ai > score_web3
    assert any("preferred theme" in r or "preferred tech" in r for r in reasons_ai)


def test_urgency_multiplier_boost():
    profile = {"preferredTags": ["AI / Machine Learning"], "preferredTechStack": ["Python"]}
    tokens = _tokenize_profile(profile)
    now = datetime.now(timezone.utc)

    urgent_hack = _make_hackathon("ai-urgent", "AI Urgent Hack", ["AI / Machine Learning"], ["Python"], HackathonMode.ONLINE, days_to_close=3)
    distant_hack = _make_hackathon("ai-distant", "AI Distant Hack", ["AI / Machine Learning"], ["Python"], HackathonMode.ONLINE, days_to_close=30)

    score_urgent, reasons_urgent = score_hackathon_for_user(tokens, profile, urgent_hack, now)
    score_distant, reasons_distant = score_hackathon_for_user(tokens, profile, distant_hack, now)

    assert score_urgent > score_distant
    assert "Registration closing soon!" in reasons_urgent


def test_recommendation_engine_ranking_order():
    engine = RecommendationEngine(default_top_n=5)
    profile = {"preferredTags": ["AI / Machine Learning"], "preferredTechStack": ["Python"], "preferredMode": "ONLINE"}

    hacks = [
        _make_hackathon("web3-1", "Web3 Hack", ["Web3"], ["Solidity"], HackathonMode.ONLINE),
        _make_hackathon("ai-1", "AI Hack", ["AI / Machine Learning"], ["Python"], HackathonMode.ONLINE),
        _make_hackathon("mobile-1", "Mobile Hack", ["Mobile"], ["Flutter"], HackathonMode.ONLINE),
    ]

    ranked = engine.fit_and_score_hackathons(profile, hacks, top_n=3)
    assert len(ranked) == 3
    assert ranked[0].hackathonId == "ai-1"  # Best match comes first
    assert ranked[0].score >= ranked[1].score >= ranked[2].score
