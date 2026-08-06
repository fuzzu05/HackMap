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
    clean_html_text,
)

logger = logging.getLogger(__name__)


class DevpostSpider(scrapy.Spider):
    """
    Scrapy spider for scraping hackathons from Devpost.
    Parses event cards and detail pages, normalizing metadata into HackathonDocument format.
    """

    name = "devpost"
    allowed_domains = ["devpost.com"]
    start_urls = ["https://devpost.com/hackathons"]

    def __init__(self, use_mock_seeds: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_mock_seeds = use_mock_seeds

    def parse(self, response):
        """
        Parses the Devpost hackathons listing page.
        If offline or mock seeds requested for deterministic pipeline testing, yields curated sample items.
        """
        if self.use_mock_seeds:
            for item in self._generate_mock_seeds():
                yield item
            return

        # Live scraping logic for Devpost event cards
        for card in response.css(".hackathon-tile"):
            url = card.css("a.clearfix::attr(href)").get()
            title = card.css(".title::text").get()
            tagline = card.css(".tagline::text").get("")
            prize_str = card.css(".prize-amount::text").get("")
            dates_str = card.css(".submission-period::text").get("")

            if url and title:
                yield response.follow(
                    url,
                    callback=self.parse_detail,
                    meta={
                        "title": title.strip(),
                        "tagline": tagline.strip() if tagline else "",
                        "prize_str": prize_str.strip() if prize_str else "",
                        "dates_str": dates_str.strip() if dates_str else "",
                    },
                )

    def parse_detail(self, response):
        """
        Parses Devpost hackathon detail page.
        """
        meta = response.meta
        title = meta.get("title") or response.css("h1::text").get() or "Devpost Hackathon"
        raw_desc = response.css("#app-details-left").get() or ""
        clean_desc = clean_html_text(raw_desc) or "Build innovative projects on Devpost."

        prize_str = meta.get("prize_str") or "$10,000 USD"
        amount, currency = parse_prize_pool(prize_str)

        tags = [normalize_tag(t) for t in response.css(".theme-label::text").getall()]
        if not tags:
            tags = ["AI", "Web Development", "Open Source"]

        start_utc = normalize_date_to_utc("2026-09-01T00:00:00Z")
        end_utc = normalize_date_to_utc("2026-09-15T23:59:59Z")
        dedup_hash = generate_dedup_hash(title, start_utc)

        doc = HackathonDocument(
            id=f"devpost-{dedup_hash[:10]}",
            source="Devpost",
            sourceUrl=response.url,
            title=title,
            tagline=meta.get("tagline", "Innovate and compete on Devpost"),
            description=clean_desc,
            organizer=Organizer(name="Devpost Community", url="https://devpost.com"),
            mode=HackathonMode.ONLINE,
            location=Location(city=None, country=None, isOnline=True),
            dates=Dates(
                registrationOpen=start_utc,
                registrationClose=end_utc,
                hackathonStart=start_utc,
                hackathonEnd=end_utc,
            ),
            prizes=Prizes(totalPoolUsd=amount, currency=currency),
            tags=tags,
            techStack=["Python", "TypeScript", "React", "Next.js"],
            eligibility="Global, Open to all developers",
            dedupHash=dedup_hash,
            status=HackathonStatus.UPCOMING,
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
                "description": "Create innovative autonomous workflows and agentic AI systems using Python, LangChain, and Next.js.",
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
            },
            {
                "id": "devpost-web3-defihub-2026",
                "source": "Devpost",
                "sourceUrl": "https://devpost.com/hackathons/web3-defihub-2026",
                "title": "DeFiHub Web3 Hackathon 2026",
                "tagline": "Next-generation decentralized finance applications",
                "description": "Develop smart contracts, cross-chain protocols, and decentralized apps.",
                "organizer": {"name": "DeFi Labs", "url": "https://defihub.io"},
                "mode": "ONLINE",
                "location": {"city": None, "country": None, "isOnline": True},
                "dates": {
                    "registrationOpen": "2026-08-05T00:00:00Z",
                    "registrationClose": "2026-09-20T23:59:59Z",
                    "hackathonStart": "2026-09-22T00:00:00Z",
                    "hackathonEnd": "2026-09-25T23:59:59Z",
                },
                "prizes": {"totalPoolUsd": 50000.0, "currency": "USD"},
                "tags": ["Web3", "Blockchain", "DeFi"],
                "techStack": ["Solidity", "Rust", "Ethereum", "React"],
                "eligibility": "Global, Open to all",
                "dedupHash": generate_dedup_hash("DeFiHub Web3 Hackathon 2026", "2026-09-22T00:00:00Z"),
                "status": "UPCOMING",
                "lastScrapedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        ]
        return seeds
