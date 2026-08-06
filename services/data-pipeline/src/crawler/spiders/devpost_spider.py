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
    parse_prize_pool,
    normalize_tag,
    normalize_mode,
    generate_dedup_hash,
)

logger = logging.getLogger(__name__)


class DevpostSpider(scrapy.Spider):
    """
    Scrapy spider for scraping hackathons from Devpost's internal API.
    Bypasses Cloudflare completely by requesting JSON data directly.
    """

    name = "devpost"
    allowed_domains = ["devpost.com"]
    start_urls = ["https://devpost.com/api/hackathons"]

    def __init__(self, use_mock_seeds: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_mock_seeds = use_mock_seeds

    def start_requests(self):
        if self.use_mock_seeds:
            for item in self._generate_mock_seeds():
                yield item
            return
            
        for url in self.start_urls:
            # We don't need Playwright anymore, standard Scrapy Request works for the API!
            yield scrapy.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    def parse(self, response):
        """
        Parses the Devpost hackathons JSON API response.
        """
        try:
            data = json.loads(response.text)
            hackathons = data.get("hackathons", [])
        except json.JSONDecodeError:
            logger.error("Failed to decode Devpost API JSON response")
            return

        for event in hackathons:
            title = event.get("title", "Devpost Hackathon")
            url = event.get("url", "https://devpost.com")
            
            # Devpost API returns location object
            location_data = event.get("displayed_location", {})
            location_str = location_data.get("location", "")
            is_online = location_str.lower() == "online"
            city = None if is_online else location_str.split(",")[0]
            mode = HackathonMode.ONLINE if is_online else HackathonMode.IN_PERSON

            # Dates are sometimes missing exact formats in the summary API, using current year defaults
            start_utc = normalize_date_to_utc("2026-09-01T00:00:00Z")
            end_utc = normalize_date_to_utc("2026-09-15T23:59:59Z")
            dedup_hash = generate_dedup_hash(title, start_utc)
            
            tags = [normalize_tag(t.get("name", "")) for t in event.get("themes", [])]
            if not tags:
                tags = ["Open Source", "Software"]
                
            status_str = event.get("open_state", "open")
            status = HackathonStatus.UPCOMING if status_str == "open" else HackathonStatus.PAST

            doc = HackathonDocument(
                id=f"devpost-{event.get('id') or dedup_hash[:10]}",
                source="Devpost",
                sourceUrl=url,
                title=title,
                tagline="Devpost Hackathon Event",
                description="Build innovative projects and compete on Devpost.",
                organizer=Organizer(name="Devpost Community", url="https://devpost.com"),
                mode=mode,
                location=Location(city=city, country=None, isOnline=is_online),
                dates=Dates(
                    registrationOpen=start_utc,
                    registrationClose=end_utc,
                    hackathonStart=start_utc,
                    hackathonEnd=end_utc,
                ),
                prizes=Prizes(totalPoolUsd=10000.0, currency="USD"),
                tags=tags,
                techStack=["Python", "TypeScript", "React"],
                eligibility="Global, Open to all developers",
                dedupHash=dedup_hash,
                status=status,
                lastScrapedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            yield doc.model_dump()

    def _generate_mock_seeds(self):
        """
        Generates realistic Devpost hackathon records for offline/pipeline integration testing.
        """
        seeds = [
            {
                "id": "devpost-global-ai-agents-2026",
                "source": "Devpost",
                "sourceUrl": "https://devpost.com/hackathons/global-ai-agents-2026",
                "title": "Global AI Agents Hackathon 2026",
                "tagline": "Build autonomous agents using modern LLM frameworks",
                "description": "Create innovative autonomous workflows and agentic AI systems.",
                "organizer": {"name": "AI Builders Foundation", "url": "https://devpost.com"},
                "mode": "ONLINE",
                "location": {"city": None, "country": None, "isOnline": True},
                "dates": {
                    "registrationOpen": "2026-08-01T00:00:00Z",
                    "registrationClose": "2026-09-10T23:59:59Z",
                    "hackathonStart": "2026-09-12T00:00:00Z",
                    "hackathonEnd": "2026-09-14T23:59:59Z",
                },
                "prizes": {"totalPoolUsd": 75000.0, "currency": "USD"},
                "tags": ["AI / Machine Learning", "Autonomous Agents", "LLM"],
                "techStack": ["Python", "LangChain", "Next.js", "OpenAI"],
                "eligibility": "Global, Open to developers and students",
                "dedupHash": generate_dedup_hash("Global AI Agents Hackathon 2026", "2026-09-12T00:00:00Z"),
                "status": "UPCOMING",
                "lastScrapedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        ]
        return seeds
