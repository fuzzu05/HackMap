from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class HackathonMode(str, Enum):
    ONLINE = "ONLINE"
    IN_PERSON = "IN_PERSON"
    HYBRID = "HYBRID"


class HackathonStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    ENDED = "ENDED"


class Organizer(BaseModel):
    name: str = Field(..., description="Name of the official hackathon organizer")
    url: Optional[str] = Field(None, description="Official website or profile of the organizer")


class Location(BaseModel):
    city: Optional[str] = Field(None, description="City where the hackathon takes place")
    country: Optional[str] = Field(None, description="Country where the hackathon takes place")
    isOnline: bool = Field(False, description="Whether remote/online participation is allowed")


class Dates(BaseModel):
    registrationOpen: str = Field(..., description="ISO-8601 UTC timestamp for registration opening")
    registrationClose: str = Field(..., description="ISO-8601 UTC timestamp for registration closing")
    hackathonStart: str = Field(..., description="ISO-8601 UTC timestamp for event start")
    hackathonEnd: str = Field(..., description="ISO-8601 UTC timestamp for event end")

    @field_validator("registrationOpen", "registrationClose", "hackathonStart", "hackathonEnd")
    @classmethod
    def validate_iso_format(cls, v: str) -> str:
        try:
            # Ensure timestamp is valid ISO 8601
            if not v.endswith("Z") and "+" not in v and "-" not in v[10:]:
                raise ValueError("Timestamp must include timezone offset or Z")
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except Exception as e:
            raise ValueError(f"Invalid ISO-8601 timestamp: {v}. Error: {str(e)}")


class Prizes(BaseModel):
    totalPoolUsd: float = Field(0.0, description="Total prize pool value normalized in USD")
    currency: str = Field("USD", description="Original or standardized currency code")


class HackathonDocument(BaseModel):
    id: str = Field(..., description="Unique slug ID for the hackathon record")
    source: str = Field(..., description="Source platform name (e.g., MLH, Devpost)")
    sourceUrl: str = Field(..., description="Original scraper URL for the hackathon")
    title: str = Field(..., description="Full title of the hackathon")
    tagline: str = Field("", description="Short tagline or summary")
    description: str = Field(..., description="Detailed description text or markdown")
    organizer: Organizer
    mode: HackathonMode
    location: Location
    dates: Dates
    prizes: Prizes
    tags: List[str] = Field(default_factory=list, description="Thematic tags (e.g., AI, Web3)")
    techStack: List[str] = Field(default_factory=list, description="Supported or featured technologies")
    eligibility: str = Field("Global, Open to all", description="Eligibility description")
    dedupHash: str = Field(..., description="Unique similarity fingerprint hash for deduplication")
    status: HackathonStatus = Field(HackathonStatus.UPCOMING, description="Lifecycle status")
    lastScrapedAt: str = Field(..., description="ISO-8601 UTC timestamp of last successful scrape")


class RankedHackathon(BaseModel):
    hackathonId: str = Field(..., description="Hackathon ID matching /hackathons/{id}")
    score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity / recommendation rank score")
    matchReasons: List[str] = Field(default_factory=list, description="Human-readable explanation for score boost")


class RecommendationDocument(BaseModel):
    updatedAt: str = Field(..., description="ISO-8601 UTC timestamp of last recommendation evaluation")
    algorithmVersion: str = Field("v1.0-hybrid-content", description="Algorithm version identifier")
    rankedHackathons: List[RankedHackathon] = Field(..., description="Ranked list of recommended hackathon items")
