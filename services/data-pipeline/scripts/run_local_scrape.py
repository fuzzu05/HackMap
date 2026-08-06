import json
import logging
import os
import sys

# Ensure src package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.crawler.spiders.devpost_spider import DevpostSpider
from src.crawler.spiders.mlh_spider import MLHSpider
from src.crawler.pipelines import HackathonValidationAndDedupPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_local_scrape")


def run_scrape_and_dedup():
    """
    Runs the live Scrapy spiders for Devpost and MLH using CrawlerProcess.
    The HackathonValidationAndDedupPipeline handles deduplication across both spiders.
    """
    logger.info("Starting Phase 2 LIVE Scrape & Deduplication pipeline...")

    # We need to tell Scrapy where our settings are
    os.environ["SCRAPY_SETTINGS_MODULE"] = "src.crawler.settings"
    settings = get_project_settings()
    
    # Overwrite some settings just to be safe for this script
    settings.set("LOG_LEVEL", "INFO")
    
    process = CrawlerProcess(settings)
    process.crawl(DevpostSpider, use_mock_seeds=False)
    process.crawl(MLHSpider, use_mock_seeds=False)
    
    # Start the reactor and block until all spiders finish
    process.start()
    
    # After process finishes, we can access the shared deduplication engine from the pipeline class
    unique_records = HackathonValidationAndDedupPipeline._shared_engine.get_deduplicated_records()
    
    logger.info("Total unique deduplicated hackathons ready for database ingestion: %d", len(unique_records))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "hackathons_dump.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([doc.model_dump() for doc in unique_records], f, indent=2)

    logger.info("Saved %d deduplicated hackathons to %s", len(unique_records), out_path)
    return unique_records


if __name__ == "__main__":
    run_scrape_and_dedup()
