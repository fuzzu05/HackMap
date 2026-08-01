import pytest
from pydantic import ValidationError
from src.models.hackathon import (
    HackathonDocument,
    HackathonMode,
    HackathonStatus,
    Organizer,
    Location,
    Dates,
    Prizes,
    RankedHackathon,
    RecommendationDocument,
)


def test_valid_hackathon_document():
    doc = HackathonDocument(
        id="mlh-global-ai-2026",
        source="MLH",
        sourceUrl="https://mlh.io/events/global-ai-2026",
        title="Global AI Hackathon 2026",
        tagline="Build the future of agents",
        description="Full hackathon details...",
        organizer=Organizer(name="MLH", url="https://mlh.io"),
        mode=HackathonMode.HYBRID,
        location=Location(city="San Francisco", country="USA", isOnline=True),
        dates=Dates(
            registrationOpen="2026-08-01T00:00:00Z",
            registrationClose="2026-09-01T00:00:00Z",
            hackathonStart="2026-09-05T00:00:00Z",
            hackathonEnd="2026-09-07T00:00:00Z",
        ),
        prizes=Prizes(totalPoolUsd=50000.0, currency="USD"),
        tags=["AI", "Python"],
        techStack=["Next.js", "Firebase", "Scrapy"],
        dedupHash="a1b2c3d4e5f6789012345678",
        status=HackathonStatus.UPCOMING,
        lastScrapedAt="2026-08-01T12:00:00Z",
    )
    assert doc.id == "mlh-global-ai-2026"
    assert doc.prizes.totalPoolUsd == 50000.0
    assert doc.mode == HackathonMode.HYBRID


def test_invalid_iso_date_raises_error():
    with pytest.raises(ValidationError):
        Dates(
            registrationOpen="2026-08-01",  # missing time and Z/offset
            registrationClose="2026-09-01T00:00:00Z",
            hackathonStart="2026-09-05T00:00:00Z",
            hackathonEnd="2026-09-07T00:00:00Z",
        )


def test_valid_recommendation_document():
    rec = RecommendationDocument(
        updatedAt="2026-08-01T12:00:00Z",
        algorithmVersion="v1.0-hybrid-content",
        rankedHackathons=[
            RankedHackathon(
                hackathonId="mlh-global-ai-2026",
                score=0.94,
                matchReasons=["Matches preferred tech: Python"],
            ),
        ],
    )
    assert len(rec.rankedHackathons) == 1
    assert rec.rankedHackathons[0].score == 0.94
