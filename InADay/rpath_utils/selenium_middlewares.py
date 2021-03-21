# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
from scrapy.utils.project import get_project_settings
from scrapy.http import TextResponse
from twisted.internet.threads import deferToThreadPool
from twisted.internet import reactor
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
from selenium.webdriver.common.proxy import Proxy, ProxyType
from urllib.request import _parse_proxy
from rpath_utils.Selenium import SeleniumRequest
from scrapy.utils.python import global_object_name
from twisted.python.failure import Failure

# Silencing remote connection debug logs
LOGGER.setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(
    logging.WARNING)

# Setting number of concurrent browser instances.
reactor.suggestThreadPoolSize(
    get_project_settings().get('CONCURRENT_REQUESTS', 16)
)

logger = logging.getLogger(__name__)

class SeleniumDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, settings):
        self.settings = settings
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if isinstance(request, SeleniumRequest) or request.meta.get('selenium', False):
            return deferToThreadPool(
                reactor, reactor.getThreadPool(), self.process_selenium_request, request,
                spider)
        else:
            return None

    def process_selenium_request(self, request, spider):
        Default_Capabilites = webdriver.ChromeOptions()
        if self.settings.get('MAXIMIZE_WINDOW', True):
            Default_Capabilites.add_argument('--start-maximized')
        if self.settings.get('RUN_HEADLESS', False):
            Default_Capabilites.add_argument('--headless')
        if self.settings.get('ENABLE_VNC', False):
            Default_Capabilites.set_capability('enableVNC', True)
        Default_Capabilites.add_argument('--silent')
        Default_Capabilites = Default_Capabilites.to_capabilities()

        SELENIUM_HUB = self.settings.get('SELENIUM_HUB', False)
        SELENIUM_DESIRED_CAPABILITIES = self.settings.get(
            'SELENIUM_DESIRED_CAPABILITIES',
            Default_Capabilites
        )

        if request.meta.get('proxy', False):
            http_proxy = Proxy()
            http_proxy.proxy_type = ProxyType.MANUAL
            # Parsing the proxy insures that we use only HOST:PORT with selenium requests
            http_proxy.http_proxy = _parse_proxy(request.meta.get('proxy'))[-1]
            http_proxy.ssl_proxy = _parse_proxy(request.meta.get('proxy'))[-1]
            http_proxy.add_to_capabilities(SELENIUM_DESIRED_CAPABILITIES)

        request.process_args['spider'] = spider

        if SELENIUM_HUB:
            driver = webdriver.Remote(command_executor=SELENIUM_HUB,
                                      desired_capabilities=SELENIUM_DESIRED_CAPABILITIES)
        else:
            driver = webdriver.Chrome(desired_capabilities=SELENIUM_DESIRED_CAPABILITIES)

        driver.set_page_load_timeout(360)

        try:
            process_results = request.selenium_process(request.url, driver, request.process_args)
        except Exception as sel_exception:
            driver.quit()
            return self.process_exception(
                request,
                sel_exception,
                spider
            )

        current_url = driver.current_url
        body = driver.page_source

        request.meta.update({'data': process_results})
        driver.quit()

        return TextResponse(current_url,
                            body=body,
                            encoding='utf-8',
                            request=request)

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
        return self._retry(request, exception, spider)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': str(reason)},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.process_args = request.process_args
            retryreq.selenium_process = request.selenium_process
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value(f'retry/reason_count/{reason}')
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.error("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': str(reason)},
                         extra={'spider': spider})
            return Failure(reason)