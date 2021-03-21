import logging
from scrapy import signals
import requests
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class CID:

    def __init__(self, settings):
        self.settings = settings
        if not self.settings.get('CID_PROCESS_ID'):
            raise NotConfigured('CID_PROCESS_ID not configured properly')
        if not self.settings.get('CID_SCHEDULER_URL'):
            raise NotConfigured('CID_SCHEDULER_URL not configured properly')

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext


    def spider_closed(self, spider):
        logger.info("Sending CID Request")
        cid_process_id = self.settings.get('CID_PROCESS_ID')
        cid_scheduler_url = self.settings.get('CID_SCHEDULER_URL')
        requests.post(cid_scheduler_url, data={'_id': cid_process_id})
        logger.info("CID Request Sent")