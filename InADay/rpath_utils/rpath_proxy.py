# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
import random

class ProxyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if self.settings.get('USE_PROXY', False):
            proxy = self.settings.get('USE_PROXY')
            if isinstance(proxy, str):
                if proxy.strip() == '':
                    self.raise_ignore_request()
                choosen_proxy = proxy
            elif isinstance(proxy, list):
                if proxy == []:
                    self.raise_ignore_request()
                choosen_proxy = random.choice(proxy)
            else:
                self.raise_ignore_request()
            request.meta['proxy'] = choosen_proxy
        else:
            return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        return None

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def raise_ignore_request(self, spider):
        spider.logger.warning('PROXY IS MISCONFIGURED, IGNORING THIS REQUEST')
        raise IgnoreRequest()