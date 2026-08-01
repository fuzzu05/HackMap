import logging
from scrapy.exceptions import DropItem
from ..models.hackathon import HackathonDocument
from ..deduplication.engine import DeduplicationEngine

logger = logging.getLogger(__name__)


class HackathonValidationAndDedupPipeline:
    """
    Scrapy item pipeline that:
    1. Validates raw scraped dictionary against Pydantic HackathonDocument schema.
    2. Runs items through the DeduplicationEngine to merge cross-listed duplicates.
    """

    def __init__(self):
        self.engine = DeduplicationEngine(similarity_threshold=0.85, date_window_days=3)

    def open_spider(self, spider):
        logger.info("HackathonValidationAndDedupPipeline opened for spider: %s", spider.name)

    def close_spider(self, spider):
        logger.info(
            "Spider %s closed. Total deduplicated unique records: %d",
            spider.name,
            len(self.engine.get_deduplicated_records()),
        )

    def process_item(self, item, spider):
        try:
            # 1. Pydantic validation
            doc = HackathonDocument.model_validate(item)
        except Exception as e:
            logger.error("Item dropped due to schema validation failure: %s", str(e))
            raise DropItem(f"Invalid HackathonDocument schema: {str(e)}")

        # 2. Deduplication processing
        merged_doc, is_duplicate = self.engine.process_record(doc)
        if is_duplicate:
            logger.info("Merged duplicate hackathon record: '%s' (%s)", merged_doc.title, merged_doc.source)
        return merged_doc.model_dump()

    def get_deduplicated_records(self):
        return self.engine.get_deduplicated_records()
