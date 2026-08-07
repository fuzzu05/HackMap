import logging
from scrapy.exceptions import DropItem
from ..models.hackathon import HackathonDocument, HackathonMode
from ..deduplication.engine import DeduplicationEngine
from ..normalization.normalizer import apply_location_jitter

logger = logging.getLogger(__name__)


class HackathonValidationAndDedupPipeline:
    """
    Scrapy item pipeline that:
    1. Validates raw scraped dictionary against Pydantic HackathonDocument schema.
    2. Runs items through the DeduplicationEngine to merge cross-listed duplicates.
    """

    _shared_engine = DeduplicationEngine(similarity_threshold=0.85, date_window_days=3)

    def __init__(self):
        self.engine = self.__class__._shared_engine

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
            
        # 3. Location Jitter for Map Plotting
        # If the event is online (or missing coordinates), scatter them deterministically
        if (merged_doc.mode == HackathonMode.ONLINE or 
            merged_doc.location.latitude is None or 
            merged_doc.location.longitude is None):
            
            lat, lng = apply_location_jitter(merged_doc.id)
            merged_doc.location.latitude = lat
            merged_doc.location.longitude = lng
            merged_doc.location.isOnline = True # Ensure it's marked online if scattered
            
        return merged_doc.model_dump()

    def get_deduplicated_records(self):
        return self.engine.get_deduplicated_records()
