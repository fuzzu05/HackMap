import pytest
from src.crawler.spiders.devpost_spider import DevpostSpider
from src.crawler.spiders.mlh_spider import MLHSpider
from src.models.hackathon import HackathonDocument


def test_devpost_spider_mock_seeds():
    spider = DevpostSpider(use_mock_seeds=True)
    seeds = spider._generate_mock_seeds()
    assert len(seeds) >= 2
    for seed in seeds:
        doc = HackathonDocument.model_validate(seed)
        assert doc.source == "Devpost"
        assert len(doc.dedupHash) > 0


def test_mlh_spider_mock_seeds():
    spider = MLHSpider(use_mock_seeds=True)
    seeds = spider._generate_mock_seeds()
    assert len(seeds) >= 2
    for seed in seeds:
        doc = HackathonDocument.model_validate(seed)
        assert doc.source == "MLH"
        assert len(doc.dedupHash) > 0
