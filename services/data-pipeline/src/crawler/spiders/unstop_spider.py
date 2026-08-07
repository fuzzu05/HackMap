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


class UnstopSpider(scrapy.Spider):
    """
    Scrapy spider for scraping hackathons from Unstop API.
    """

    name = "unstop"
    allowed_domains = ["unstop.com"]
    start_urls = ["https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&page=1&per_page=150&oppstatus=open&sortBy=&orderBy=&filter_condition=&undefined=true"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, 
                headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )

    def parse(self, response):
        try:
            payload = json.loads(response.text)
            data = payload.get("data", {})
            hackathons = data.get("data", [])
        except json.JSONDecodeError:
            logger.error("Failed to decode Unstop API JSON response")
            return
            
        # Pagination
        if "&page=1&" in response.url:
            last_page = data.get("last_page", 1)
            for page in range(2, last_page + 1):
                next_url = response.url.replace("&page=1&", f"&page={page}&")
                yield scrapy.Request(next_url, headers=response.request.headers)

        for event in hackathons:
            title = event.get("title", "Unstop Hackathon")
            public_url = event.get("public_url", "")
            url = f"https://unstop.com/{public_url}" if public_url else "https://unstop.com"
            
            region = event.get("region", "online")
            is_online = region.lower() == "online"
            city = None if is_online else region
            mode = HackathonMode.ONLINE if is_online else HackathonMode.IN_PERSON

            start_utc = normalize_date_to_utc(event.get("regn_open_date") or "2026-09-01T00:00:00Z")
            end_utc = normalize_date_to_utc(event.get("regn_close_date") or "2026-09-15T23:59:59Z")
            
            dedup_hash = generate_dedup_hash(title, start_utc)
            
            tags = [normalize_tag(t) for t in event.get("categories", ["Hackathon"])]
            
            organizer_name = event.get("organization_name", "Unstop Community")

            doc = HackathonDocument(
                id=f"unstop-{event.get('id') or dedup_hash[:10]}",
                source="Unstop",
                sourceUrl=url,
                title=title,
                tagline="Unstop Hackathon",
                description="Participate in hackathons hosted on Unstop.",
                organizer=Organizer(name=organizer_name, url="https://unstop.com"),
                mode=mode,
                location=Location(city=city, country="India" if not is_online else None, isOnline=is_online),
                dates=Dates(
                    registrationOpen=start_utc,
                    registrationClose=end_utc,
                    hackathonStart=start_utc,
                    hackathonEnd=end_utc,
                ),
                prizes=Prizes(totalPoolUsd=1000.0, currency="USD"),
                tags=tags,
                techStack=["Open Source"],
                eligibility="Open to all",
                dedupHash=dedup_hash,
                status=HackathonStatus.ONGOING,
                lastScrapedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            yield doc.model_dump()
