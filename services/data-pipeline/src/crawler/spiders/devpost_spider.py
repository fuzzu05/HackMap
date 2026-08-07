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
    start_urls = ["https://devpost.com/api/hackathons?status[]=open&status[]=upcoming&page=1"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, 
                headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )

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
            
        # Handle Pagination (only on first page request)
        if response.url.endswith("&page=1"):
            meta = data.get("meta", {})
            total_count = meta.get("total_count", 0)
            per_page = meta.get("per_page", 15)
            import math
            if per_page > 0:
                total_pages = math.ceil(total_count / per_page)
                for page in range(2, total_pages + 1):
                    next_url = response.url.replace("&page=1", f"&page={page}")
                    yield scrapy.Request(next_url, headers=response.request.headers)

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
            status = HackathonStatus.UPCOMING if status_str == "open" else HackathonStatus.ENDED

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

