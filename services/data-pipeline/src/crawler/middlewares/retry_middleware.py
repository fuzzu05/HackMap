import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

logger = logging.getLogger(__name__)


class ExponentialRetryMiddleware(RetryMiddleware):
    """
    Custom retry middleware handling 429 Too Many Requests and 5xx server errors
    with logging and exponential backoff behavior.
    """

    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint("RETRY_TIMES", 3)
        self.retry_http_codes = set(int(x) for x in settings.getlist("RETRY_HTTP_CODES", [429, 500, 502, 503, 504, 522, 524]))

    def process_response(self, request, response, spider):
        if request.meta.get("dont_retry", False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            spider.logger.warning(
                "Retrying %s (failed 1 times): HTTP %s", request.url, response.status
            )
            return self._retry(request, reason, spider) or response
        return response
