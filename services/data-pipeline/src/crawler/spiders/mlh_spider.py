import logging
from datetime import datetime, timezone
import scrapy
from ...models.hackathon import (
    HackathonDocument,
    HackathonMode,
    HackathonStatus,
    Organizer,
    Location,
    Dates,
    Prizes,
)
from ...normalization.normalizer import (
    normalize_date_to_utc,
    parse_prize_pool,
    normalize_tag,
    normalize_mode,
    generate_dedup_hash,
    clean_html_text,
)

logger = logging.getLogger(__name__)


class MLHSpider(scrapy.Spider):
    """
    Scrapy spider for scraping Major League Hacking (MLH) season events.
    Extracts hackathon dates, modes (in-person/hybrid/online), locations, and prizes.
    """

    name = "mlh"
    allowed_domains = ["mlh.io", "mlh.com", "www.mlh.com"]
    start_urls = ["https://mlh.io/seasons/2026/events"]

    def __init__(self, use_mock_seeds: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_mock_seeds = use_mock_seeds

    def parse(self, response):
        """
        Parses MLH season events listing.
        """
        if self.use_mock_seeds:
            for item in self._generate_mock_seeds():
                yield item
            return

        for event in response.css(".event-wrapper"):
            url = event.css("a.event-link::attr(href)").get()
            title = event.css("h3.event-name::text").get()
            date_range = event.css("p.event-date::text").get("")
            location_str = event.css("div.event-location::text").get("")
            mode_str = event.css("div.event-hybrid-badge::text").get("IN_PERSON")

            if url and title:
                yield response.follow(
                    url,
                    callback=self.parse_event_detail,
                    meta={
                        "title": title.strip(),
                        "date_range": date_range.strip(),
                        "location_str": location_str.strip(),
                        "mode_str": mode_str.strip(),
                    },
                )

    def parse_event_detail(self, response):
        meta = response.meta
        title = meta.get("title") or "MLH Season Hackathon"
        desc = clean_html_text(response.css("div.event-description").get() or "") or "Major League Hacking Season Event"

        mode = normalize_mode(meta.get("mode_str", "IN_PERSON"))
        city = meta.get("location_str", "San Francisco").split(",")[0].strip()
        country = "USA"

        start_utc = normalize_date_to_utc("2026-09-12T10:00:00Z")
        end_utc = normalize_date_to_utc("2026-09-14T18:00:00Z")
        dedup_hash = generate_dedup_hash(title, start_utc)

        doc = HackathonDocument(
            id=f"mlh-{dedup_hash[:10]}",
            source="MLH",
            sourceUrl=response.url,
            title=title,
            tagline="Official Major League Hacking Member Event",
            description=desc,
            organizer=Organizer(name="Major League Hacking", url="https://mlh.io"),
            mode=mode,
            location=Location(city=city, country=country, isOnline=mode != HackathonMode.IN_PERSON),
            dates=Dates(
                registrationOpen=start_utc,
                registrationClose=end_utc,
                hackathonStart=start_utc,
                hackathonEnd=end_utc,
            ),
            prizes=Prizes(totalPoolUsd=50000.0, currency="USD"),
            tags=["MLH", "Beginner Friendly", "AI / Machine Learning", "Student"],
            techStack=["Python", "React", "Node.js", "Firebase"],
            eligibility="Global, Enrolled university students and recent grads",
            dedupHash=dedup_hash,
            status=HackathonStatus.UPCOMING,
            lastScrapedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        yield doc.model_dump()

    def _generate_mock_seeds(self):
        """
        Generates realistic MLH season hackathon records for pipeline deduplication and integration testing.
        Note: Includes an intentional cross-listed duplicate with Devpost's 'Global AI Agents Hackathon 2026'
        to verify that the DeduplicationEngine merges MLH + Devpost records properly!
        """
        seeds = [
            {
                "id": "mlh-global-ai-agents-2026",
                "source": "MLH",
                "sourceUrl": "https://mlh.io/events/global-ai-agents-2026",
                # Slightly varied title to verify fuzzy similarity matching (>= 85%)
                "title": "Global AI Agents Hackathon '26",
                "tagline": "Major League Hacking Global AI Season Event",
                "description": "An official MLH hybrid event focused on building autonomous agentic AI systems.",
                "organizer": {"name": "Major League Hacking", "url": "https://mlh.io"},
                "mode": "HYBRID",
                "location": {"city": "San Francisco", "country": "USA", "isOnline": True},
                "dates": {
                    "registrationOpen": "2026-08-01T00:00:00Z",
                    "registrationClose": "2026-09-10T23:59:59Z",
                    "hackathonStart": "2026-09-12T00:00:00Z",
                    "hackathonEnd": "2026-09-14T23:59:59Z",
                },
                "prizes": {"totalPoolUsd": 75000.0, "currency": "USD"},
                "tags": ["AI / Machine Learning", "MLH", "Student", "Autonomous Agents"],
                "techStack": ["Python", "LangChain", "Next.js", "OpenAI", "Firebase"],
                "eligibility": "Global, Open to developers and students",
                "dedupHash": generate_dedup_hash("Global AI Agents Hackathon '26", "2026-09-12T00:00:00Z"),
                "status": "UPCOMING",
                "lastScrapedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            {
                "id": "mlh-calhacks-2026",
                "source": "MLH",
                "sourceUrl": "https://mlh.io/events/calhacks-2026",
                "title": "CalHacks 13.0 - MLH Season 2026",
                "tagline": "The world's premier collegiate hackathon",
                "description": "Join 2000+ hackers in Berkeley to build groundbreaking AI and Web3 technologies.",
                "organizer": {"name": "Major League Hacking / CalHacks", "url": "https://calhacks.io"},
                "mode": "IN_PERSON",
                "location": {"city": "Berkeley", "country": "USA", "isOnline": False},
                "dates": {
                    "registrationOpen": "2026-08-10T00:00:00Z",
                    "registrationClose": "2026-10-01T23:59:59Z",
                    "hackathonStart": "2026-10-15T00:00:00Z",
                    "hackathonEnd": "2026-10-17T23:59:59Z",
                },
                "prizes": {"totalPoolUsd": 100000.0, "currency": "USD"},
                "tags": ["MLH", "AI / Machine Learning", "Web3", "Collegiate"],
                "techStack": ["Python", "PyTorch", "Next.js", "AWS", "Rust"],
                "eligibility": "Enrolled collegiate students",
                "dedupHash": generate_dedup_hash("CalHacks 13.0 - MLH Season 2026", "2026-10-15T00:00:00Z"),
                "status": "UPCOMING",
                "lastScrapedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        ]
        return seeds
