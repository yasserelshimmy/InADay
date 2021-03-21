# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.project import get_project_settings
from urllib.parse import urljoin


class InadaySpider(scrapy.Spider):
    name = 'inaday'
    settings = get_project_settings()
    urls = ['http://www.inaday.sa/'] * 100
    # urls = ['http://www.inaday.sa/'] * 1
    allowed_domains = ['inaday.sa']
    # url = 'https://www.abc.com'

    # filepath = settings.get('INPUT_FILE_PATH')
    # records = csv_to_records(filepath)

    # def __init__(self, default_arg='<arg_val>', *args, **kwargs):
    #     super(InadaySpider, self).__init__(*args, **kwargs)
    #     self.default_arg = default_arg

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(
                url=url,
                meta={'dont_redirect': True},
                dont_filter=True,
            )

    def parse(self, response):
        try:
            all_urls = response.xpath('//*[contains(@href, "inaday") or contains(@src, "inaday")]')
            for url in all_urls:
                temp_url = url.attrib.get('href', url.attrib.get('src'))
                concated_url = urljoin(response.url, temp_url)
                yield scrapy.Request(
                    url=concated_url,
                    meta={'dont_redirect': True},
                    dont_filter=True,
                )
        except:
            pass