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
    normalize_tag,
    generate_dedup_hash,
)

logger = logging.getLogger(__name__)


class DoraHacksSpider(scrapy.Spider):
    """
    Scrapy spider for scraping hackathons from DoraHacks API.
    """

    name = "dorahacks"
    allowed_domains = ["dorahacks.io"]
    start_urls = [
        "https://dorahacks.io/api/v1/hub/hackathons?page=1&page_size=24&status=ongoing",
        "https://dorahacks.io/api/v1/hub/hackathons?page=1&page_size=24&status=upcoming"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, 
                headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )

    def parse(self, response):
        try:
            data = json.loads(response.text)
            hackathons = data.get("results", [])
        except json.JSONDecodeError:
            logger.error("Failed to decode DoraHacks API JSON response")
            return
            
        # Pagination
        if "page=1&" in response.url:
            total_count = data.get("count", 0)
            import math
            total_pages = math.ceil(total_count / 24)
            for page in range(2, total_pages + 1):
                next_url = response.url.replace("page=1&", f"page={page}&")
                yield scrapy.Request(next_url, headers=response.request.headers)

        current_time = datetime.now().timestamp()

        for event in hackathons:
            timeline_end = event.get("timeline_end", 0)
            
            # Skip past hackathons to only get active/upcoming
            if timeline_end and timeline_end < current_time:
                continue

            title = event.get("title", "DoraHacks Hackathon")
            uname = event.get("uname", "")
            url = f"https://dorahacks.io/hackathon/{uname}"
            
            venue_form = event.get("venue_form", "Virtual")
            is_online = venue_form.lower() == "virtual"
            city = event.get("venue_city_id") or "Virtual"
            country = event.get("venue_country_id")
            mode = HackathonMode.ONLINE if is_online else HackathonMode.IN_PERSON

            # Convert unix timestamps to UTC strings
            timeline_start = event.get("timeline_start")
            start_utc = normalize_date_to_utc(datetime.fromtimestamp(timeline_start).isoformat()) if timeline_start else normalize_date_to_utc("2026-09-01T00:00:00Z")
            end_utc = normalize_date_to_utc(datetime.fromtimestamp(timeline_end).isoformat()) if timeline_end else normalize_date_to_utc("2026-09-15T23:59:59Z")
            
            dedup_hash = generate_dedup_hash(title, start_utc)
            
            tags_raw = event.get("tags", "")
            tags = [normalize_tag(t.strip()) for t in tags_raw.split(",")] if tags_raw else ["Web3", "Blockchain"]
            
            ecosystem_raw = event.get("ecosystem", "")
            tech_stack = [t.strip() for t in ecosystem_raw.split(",")] if ecosystem_raw else ["Solidity", "Rust", "Web3"]
                
            status = HackathonStatus.UPCOMING if timeline_start and timeline_start > current_time else HackathonStatus.ONGOING

            owner = event.get("owner", {})
            organizer_name = owner.get("name", "DoraHacks Community")

            doc = HackathonDocument(
                id=f"dorahacks-{event.get('id') or dedup_hash[:10]}",
                source="DoraHacks",
                sourceUrl=url,
                title=title,
                tagline="DoraHacks Web3 Hackathon",
                description="Build innovative Web3 projects and compete on DoraHacks.",
                organizer=Organizer(name=organizer_name, url="https://dorahacks.io"),
                mode=mode,
                location=Location(city=city if not is_online else None, country=country if not is_online else None, isOnline=is_online),
                dates=Dates(
                    registrationOpen=start_utc,
                    registrationClose=end_utc,
                    hackathonStart=start_utc,
                    hackathonEnd=end_utc,
                ),
                prizes=Prizes(totalPoolUsd=float(event.get("bonus_price", 0)), currency=event.get("bonus_token", "USD")),
                tags=tags,
                techStack=tech_stack,
                eligibility="Global, Open to all developers",
                dedupHash=dedup_hash,
                status=status,
                lastScrapedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            yield doc.model_dump()
