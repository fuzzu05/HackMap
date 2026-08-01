import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple
from ..models.hackathon import HackathonDocument

logger = logging.getLogger(__name__)


def compute_title_similarity(title1: str, title2: str) -> float:
    """
    Computes a composite similarity score (0.0 to 1.0) between two hackathon titles
    using difflib SequenceMatcher combined with Jaccard token overlap.
    """
    if not title1 or not title2:
        return 0.0

    t1_clean = re.sub(r"[^a-z0-9\s]", "", title1.lower()).strip()
    t2_clean = re.sub(r"[^a-z0-9\s]", "", title2.lower()).strip()

    # Sequence matcher ratio
    seq_ratio = SequenceMatcher(None, t1_clean, t2_clean).ratio()

    # Token Jaccard similarity
    tokens1 = set(t1_clean.split())
    tokens2 = set(t2_clean.split())
    if not tokens1 or not tokens2:
        return seq_ratio

    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    jaccard = intersection / union if union > 0 else 0.0

    # Return weighted average of string similarity and token similarity
    return round((seq_ratio * 0.6) + (jaccard * 0.4), 4)


def _days_between(date_str1: str, date_str2: str) -> float:
    """
    Calculates absolute difference in days between two ISO-8601 UTC timestamp strings.
    """
    try:
        dt1 = datetime.fromisoformat(date_str1.replace("Z", "+00:00"))
        dt2 = datetime.fromisoformat(date_str2.replace("Z", "+00:00"))
        return abs((dt1 - dt2).total_seconds()) / (24 * 3600)
    except Exception:
        return 999.0


def merge_hackathon_records(primary: HackathonDocument, secondary: HackathonDocument) -> HackathonDocument:
    """
    Merges two cross-listed HackathonDocument instances (e.g. MLH and Devpost listings)
    into a single enriched document, prioritizing richer metadata.
    """
    # Merge tags & tech stack while preserving order and uniqueness
    combined_tags = list(dict.fromkeys(primary.tags + secondary.tags))
    combined_tech = list(dict.fromkeys(primary.techStack + secondary.techStack))

    # Retain richer description
    best_desc = primary.description if len(primary.description) >= len(secondary.description) else secondary.description
    best_tagline = primary.tagline if len(primary.tagline) >= len(secondary.tagline) else secondary.tagline

    # Retain higher prize pool if available
    best_prizes = primary.prizes
    if secondary.prizes.totalPoolUsd > primary.prizes.totalPoolUsd:
        best_prizes = secondary.prizes

    # Prefer specific city/country location over empty
    best_location = primary.location
    if not primary.location.city and secondary.location.city:
        best_location = secondary.location

    merged = HackathonDocument(
        id=primary.id,
        source=f"{primary.source}+{secondary.source}" if secondary.source not in primary.source else primary.source,
        sourceUrl=primary.sourceUrl,
        title=primary.title,
        tagline=best_tagline,
        description=best_desc,
        organizer=primary.organizer,
        mode=primary.mode,
        location=best_location,
        dates=primary.dates,
        prizes=best_prizes,
        tags=combined_tags,
        techStack=combined_tech,
        eligibility=primary.eligibility,
        dedupHash=primary.dedupHash,
        status=primary.status,
        lastScrapedAt=max(primary.lastScrapedAt, secondary.lastScrapedAt),
    )
    logger.info("Merged hackathon records: '%s' (%s) + '%s' (%s)", primary.title, primary.source, secondary.title, secondary.source)
    return merged


class DeduplicationEngine:
    """
    In-memory and scalable deduplication engine that identifies exact URL/hash duplicates
    and fuzzy title/date matches, merging records automatically.
    """

    def __init__(self, similarity_threshold: float = 0.85, date_window_days: int = 3):
        self.similarity_threshold = similarity_threshold
        self.date_window_days = date_window_days
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Dict[str, HackathonDocument] = {}
        self.records: List[HackathonDocument] = []

    def process_record(self, doc: HackathonDocument) -> Tuple[HackathonDocument, bool]:
        """
        Processes a candidate HackathonDocument.
        Returns (document, is_duplicate):
        - If duplicate found: merges with existing record and returns (merged_doc, True).
        - If unique: registers record and returns (doc, False).
        """
        # 1. Check exact URL match
        if doc.sourceUrl in self.seen_urls:
            logger.debug("Exact URL duplicate skipped: %s", doc.sourceUrl)
            return doc, True

        # 2. Check exact dedupHash match
        if doc.dedupHash in self.seen_hashes:
            existing = self.seen_hashes[doc.dedupHash]
            merged = merge_hackathon_records(existing, doc)
            self._update_index(existing, merged)
            return merged, True

        # 3. Fuzzy match against existing records within date window
        for existing in self.records:
            days_diff = _days_between(existing.dates.hackathonStart, doc.dates.hackathonStart)
            if days_diff <= self.date_window_days:
                similarity = compute_title_similarity(existing.title, doc.title)
                if similarity >= self.similarity_threshold:
                    logger.info(
                        "Fuzzy match (similarity=%.2f) between '%s' and '%s'",
                        similarity,
                        existing.title,
                        doc.title,
                    )
                    merged = merge_hackathon_records(existing, doc)
                    self._update_index(existing, merged)
                    return merged, True

        # Unique record
        self.seen_urls.add(doc.sourceUrl)
        self.seen_hashes[doc.dedupHash] = doc
        self.records.append(doc)
        return doc, False

    def _update_index(self, old_doc: HackathonDocument, new_doc: HackathonDocument):
        """
        Updates in-memory registry after a merge.
        """
        if old_doc in self.records:
            idx = self.records.index(old_doc)
            self.records[idx] = new_doc
        self.seen_hashes[new_doc.dedupHash] = new_doc
        self.seen_urls.add(new_doc.sourceUrl)

    def get_deduplicated_records(self) -> List[HackathonDocument]:
        return self.records
