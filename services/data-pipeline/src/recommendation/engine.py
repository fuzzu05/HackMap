import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from ..models.hackathon import HackathonDocument, RankedHackathon

logger = logging.getLogger(__name__)


def _tokenize_profile(profile: Dict) -> Set[str]:
    """
    Extracts lowercase normalized tokens from user profile preferences.
    """
    tokens = set()
    for tag in profile.get("preferredTags", []):
        tokens.update(tag.lower().split())
    for tech in profile.get("preferredTechStack", []):
        tokens.update(tech.lower().split())
    if "preferredMode" in profile:
        tokens.add(str(profile["preferredMode"]).lower())
    return {t for t in tokens if len(t) > 1}


def _tokenize_hackathon(doc: HackathonDocument) -> Set[str]:
    """
    Extracts lowercase normalized tokens from a hackathon document.
    """
    tokens = set()
    for tag in doc.tags:
        tokens.update(tag.lower().split())
    for tech in doc.techStack:
        tokens.update(tech.lower().split())
    tokens.add(doc.mode.value.lower())
    return {t for t in tokens if len(t) > 1}


def score_hackathon_for_user(
    profile_tokens: Set[str],
    user_profile: Dict,
    doc: HackathonDocument,
    current_utc: datetime,
) -> Tuple[float, List[str]]:
    """
    Calculates content similarity score (0.0 to 1.0) and urgency multiplier for a hackathon
    relative to a user's preferences, generating human-readable match reasons.
    """
    match_reasons: List[str] = []
    hack_tokens = _tokenize_hackathon(doc)

    # Calculate Jaccard / token overlap similarity
    if not profile_tokens or not hack_tokens:
        base_score = 0.50
    else:
        intersection = profile_tokens.intersection(hack_tokens)
        if intersection:
            # Match percentage boosted towards 1.0 based on overlap count
            base_score = min(0.40 + (len(intersection) * 0.15), 0.90)
        else:
            base_score = 0.30

    # Add reason strings for matching tags and tech stack
    matching_tags = [
        t for t in doc.tags if any(pt.lower() in t.lower() for pt in user_profile.get("preferredTags", []))
    ]
    if matching_tags:
        match_reasons.append(f"Matches preferred theme: {', '.join(matching_tags[:2])}")

    matching_tech = [
        ts for ts in doc.techStack if any(pt.lower() in ts.lower() for pt in user_profile.get("preferredTechStack", []))
    ]
    if matching_tech:
        match_reasons.append(f"Matches preferred tech: {', '.join(matching_tech[:2])}")

    # Mode match check
    pref_mode = str(user_profile.get("preferredMode", "")).upper()
    if pref_mode and pref_mode == doc.mode.value:
        base_score = min(base_score + 0.05, 0.95)
        match_reasons.append(f"Preferred event format ({doc.mode.value})")

    # Time-Decay / Urgency Multiplier check
    try:
        reg_close_dt = datetime.fromisoformat(doc.dates.registrationClose.replace("Z", "+00:00"))
        days_left = (reg_close_dt - current_utc).total_seconds() / (24 * 3600)
        if 0 <= days_left <= 7:
            base_score = min(base_score * 1.15, 0.99)
            match_reasons.append("Registration closing soon!")
        elif 7 < days_left <= 14:
            base_score = min(base_score * 1.08, 0.95)
    except Exception:
        pass

    if not match_reasons:
        match_reasons.append("Recommended upcoming hackathon")

    return round(base_score, 4), match_reasons


class RecommendationEngine:
    """
    Personalization engine that evaluates user profile vectors against hackathon records,
    ranking items and generating human-readable match explanations.
    """

    def __init__(self, default_top_n: int = 10):
        self.default_top_n = default_top_n

    def fit_and_score_hackathons(
        self,
        user_profile: Dict,
        hackathons: List[HackathonDocument],
        top_n: int = 10,
    ) -> List[RankedHackathon]:
        """
        Returns top_n RankedHackathon items sorted by descending score.
        """
        current_utc = datetime.now(timezone.utc)
        profile_tokens = _tokenize_profile(user_profile)

        scored_items: List[RankedHackathon] = []
        for doc in hackathons:
            score, reasons = score_hackathon_for_user(
                profile_tokens=profile_tokens,
                user_profile=user_profile,
                doc=doc,
                current_utc=current_utc,
            )
            scored_items.append(
                RankedHackathon(
                    hackathonId=doc.id,
                    score=score,
                    matchReasons=reasons,
                )
            )

        # Sort by score descending
        scored_items.sort(key=lambda r: r.score, reverse=True)
        return scored_items[:top_n]
