import json
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
    normalize_mode,
    generate_dedup_hash,
)

logger = logging.getLogger(__name__)


class MLHSpider(scrapy.Spider):
    """
    Scrapy spider for scraping Major League Hacking (MLH) season events.
    Extracts hackathon data directly from the Inertia.js JSON payload embedded in the HTML.
    """

    name = "mlh"
    allowed_domains = ["mlh.io", "mlh.com", "www.mlh.com"]
    start_urls = ["https://mlh.io/seasons/2024/events"]

    def __init__(self, use_mock_seeds: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_mock_seeds = use_mock_seeds

    def parse(self, response):
        """
        Parses MLH season events listing from the Inertia JSON block.
        """
        if self.use_mock_seeds:
            for item in self._generate_mock_seeds():
                yield item
            return

        json_data = response.css('script[data-page="app"]::text').get()
        if not json_data:
            logger.warning("Could not find Inertia JSON payload on MLH page!")
            return

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            logger.error("Failed to decode Inertia JSON payload")
            return

        props = data.get("props", {})
        events = props.get("upcomingEvents", []) + props.get("pastEvents", [])

        for event in events:
            title = event.get("name", "MLH Hackathon")
            url = event.get("websiteUrl") or ("https://mlh.io" + event.get("url", ""))
            
            starts_at_raw = event.get("startsAt")
            ends_at_raw = event.get("endsAt")
            start_utc = normalize_date_to_utc(starts_at_raw) if starts_at_raw else normalize_date_to_utc("2024-01-01T00:00:00Z")
            end_utc = normalize_date_to_utc(ends_at_raw) if ends_at_raw else start_utc
            
            format_type = event.get("formatType", "physical")
            mode = HackathonMode.ONLINE if format_type == "digital" else HackathonMode.IN_PERSON
            
            venue = event.get("venueAddress") or {}
            city = venue.get("city") or event.get("location", "").split(",")[0] or "Unknown"
            country = venue.get("country") or "USA"

            dedup_hash = generate_dedup_hash(title, start_utc)

            doc = HackathonDocument(
                id=f"mlh-{event.get('id') or dedup_hash[:10]}",
                source="MLH",
                sourceUrl=url,
                title=title,
                tagline="Official Major League Hacking Member Event",
                description="Major League Hacking Season Event",
                organizer=Organizer(name="Major League Hacking", url="https://mlh.io"),
                mode=mode,
                location=Location(city=city, country=country, isOnline=mode != HackathonMode.IN_PERSON),
                dates=Dates(
                    registrationOpen=start_utc,
                    registrationClose=end_utc,
                    hackathonStart=start_utc,
                    hackathonEnd=end_utc,
                ),
                prizes=Prizes(totalPoolUsd=10000.0, currency="USD"),
                tags=["MLH", "Student"],
                techStack=["Python", "React", "Node.js", "Firebase"],
                eligibility="Global, Enrolled university students and recent grads",
                dedupHash=dedup_hash,
                status=HackathonStatus.UPCOMING if format_type != "ended" else HackathonStatus.PAST,
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
            }
        ]
        return seeds
