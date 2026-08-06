# Scrapy settings for HackMap Data Pipeline
BOT_NAME = "hackmap_crawler"

SPIDER_MODULES = ["src.crawler.spiders"]
NEWSPIDER_MODULE = "src.crawler.spiders"

# Respect robots.txt rules by default
ROBOTSTXT_OBEY = True

# Concurrent requests and delays for polite scraping
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True

# Cookie management
COOKIES_ENABLED = False

# Enable custom User-Agent rotation and Retry middlewares
DOWNLOADER_MIDDLEWARES = {
    "src.crawler.middlewares.user_agent.RotateUserAgentMiddleware": 400,
    "src.crawler.middlewares.retry_middleware.ExponentialRetryMiddleware": 550,
}

# Enable Validation and Deduplication Item Pipeline
ITEM_PIPELINES = {
    "src.crawler.pipelines.HackathonValidationAndDedupPipeline": 300,
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Enable asynchronous reactor (Required for Playwright)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Playwright Configuration
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}
