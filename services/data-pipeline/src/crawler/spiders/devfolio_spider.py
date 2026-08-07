import json
import logging
from datetime import datetime, timezone
import scrapy
from scrapy.http import JsonRequest
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
    generate_dedup_hash,
)

import logging
import urllib.request
from twisted.internet import threads

logger = logging.getLogger(__name__)

class DevfolioSpider(scrapy.Spider):
    """
    Scrapy spider for scraping hackathons from Devfolio's search API.
    Bypasses Scrapy downloader due to POST/GET redirect issues.
    Uses twisted deferToThread to prevent blocking the reactor.
    """

    name = "devfolio"
    allowed_domains = ["api.devfolio.co"]
    
    search_types = ["application_open", "upcoming"]

    def start_requests(self):
        # We start with a dummy request to jump into Scrapy's callback loop
        yield scrapy.Request('data:,', dont_filter=True, callback=self.kick_off_threads)

    def kick_off_threads(self, response):
        for t in self.search_types:
            # Dispatch background threads so we don't block Twisted
            deferred = threads.deferToThread(self.fetch_all_devfolio, t)
            deferred.addCallback(self.handle_thread_result, search_type=t)
            deferred.addErrback(self.handle_thread_error, search_type=t)

    def fetch_all_devfolio(self, t):
        current_from = 0
        size = 100
        all_hackathons = []
        
        while True:
            payload = {
                "type": t,
                "from": current_from,
                "size": size
            }
            req = urllib.request.Request(
                'https://api.devfolio.co/api/search/hackathons', 
                data=json.dumps(payload).encode('utf-8'),
                headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                hits_obj = data.get("hits", {})
                total = hits_obj.get("total", {}).get("value", 0)
                batch = [hit.get("_source", {}) for hit in hits_obj.get("hits", [])]
                all_hackathons.extend(batch)
                
                current_from += size
                if current_from >= total:
                    break
        return all_hackathons

    def handle_thread_result(self, hackathons, search_type):
        for doc in self.parse_hackathons(hackathons, search_type):
            self.crawler.engine.crawl(doc, self)
            
    def handle_thread_error(self, failure, search_type):
        logger.error(f"Devfolio API failed for {search_type}: {failure.getErrorMessage()}")

    def parse_hackathons(self, hackathons, search_type):
        for event in hackathons:
            title = event.get("name", "Devfolio Hackathon")
            slug = event.get("slug", "")
            url = f"https://{slug}.devfolio.co" if slug else "https://devfolio.co"
            
            is_online = event.get("is_online", False)
            city = event.get("city")
            country = event.get("country")
            mode = HackathonMode.ONLINE if is_online else HackathonMode.IN_PERSON

            start_utc = normalize_date_to_utc(event.get("starts_at") or "2026-09-01T00:00:00Z")
            end_utc = normalize_date_to_utc(event.get("ends_at") or "2026-09-15T23:59:59Z")
            
            dedup_hash = generate_dedup_hash(title, start_utc)
            
            status = HackathonStatus.UPCOMING if search_type == "upcoming" else HackathonStatus.ONGOING

            doc = HackathonDocument(
                id=f"devfolio-{event.get('uuid') or dedup_hash[:10]}",
                source="Devfolio",
                sourceUrl=url,
                title=title,
                tagline="Devfolio Hackathon",
                description="Participate in hackathons hosted on Devfolio.",
                organizer=Organizer(name="Devfolio", url="https://devfolio.co"),
                mode=mode,
                location=Location(city=city if not is_online else None, country=country if not is_online else None, isOnline=is_online),
                dates=Dates(
                    registrationOpen=start_utc,
                    registrationClose=end_utc,
                    hackathonStart=start_utc,
                    hackathonEnd=end_utc,
                ),
                prizes=Prizes(totalPoolUsd=5000.0, currency="USD"),
                tags=["Web3", "Blockchain", "Open Source"],
                techStack=["JavaScript", "React"],
                eligibility="Open to all",
                dedupHash=dedup_hash,
                status=status,
                lastScrapedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            yield doc.model_dump()
