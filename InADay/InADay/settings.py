# -*- coding: utf-8 -*-

# Scrapy settings for InADay project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'InADay'

SPIDER_MODULES = ['InADay.spiders']
NEWSPIDER_MODULE = 'InADay.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'InADay (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'InADay.middlewares.InadaySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
#     'rpath_utils.ProxyDownloaderMiddleware': 100,
#     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#     'rpath_utils.SeleniumDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     'rpath_utils.DefaultPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

##########################

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
}

FIELDS_TO_EXPORT = []

INPUT_FILE_PATH = 'data/input/InADay.csv'
OUTPUT_FILE_DIR = 'data/output'
LOG_FILE_DIR = 'data/log'

RETRY_TIMES = 5

EXTENSIONS = {
   'rpath_utils.extensions.Notify': 500,
}

NOTIFICATION_CONFIG = {
    "smtphost": "smtp-mail.outlook.com",
    "mailfrom": "webtapstatus@telogical.com",
    "smtpuser": "webtapstatus@telogical.com",
    "smtppass": "B)TGn7Z&#",
    "smtpport": 587,
    "smtptls": True,
    "smtpssl": False,
}

NOTIFICATION_EMAIL = {
    'subject': "InADay's {TODAY} run finished",
    'body': [
        "<h4>Hello There!</h4>\n"
        "<p>Your files are ready.</p>\n",
        "<p>FILES:</p>\n",
        "<p style='text-indent: 30px;'>{FILES}</p>\n",
        "<p>Thank you, and have a pleasant day.</p>\n",
        "<sub>Contact Yasser Elshimmy at yelshimmy@telogical.com",
        " to stop receiving this or for adding other people.</sub>",
    ],
    'to': "",
    'cc': [
        "yasserelshimmy@gmail.com",
        # "yelshimmy@telogical.com",
        # "TeamOperationsFT@telogical.com",
        # "amurphy@telogical.com",
        # "rbeckman@telogical.com",
        # "jbrown@telogical.com",
        # "evandermark@telogical.com",
        # "rbrennan@telogical.com",
    ],
    "bcc": [],
    "mimetype": "html",
    "attach_output": False,
}
