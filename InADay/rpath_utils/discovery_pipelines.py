# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pandas as pd
import numpy as np
from scrapy.exceptions import NotConfigured, DropItem
from rpath_utils.csv_handler import csv_to_records
import re
import logging

logger = logging.getLogger(__name__)


def normalize_and_match(x1: str, x2: str) -> bool:
    return x1.lower().strip() == x2.lower().strip()


class DiscoveryPipeline(object):

    def __init__(self, settings, spider):
        self.settings = settings
        if not self.settings.get('FEED_KEYWORDS_FILE_PATH'):
            raise NotConfigured('FEED_KEYWORDS_FILE_PATH is not configured properly')
        if not self.settings.get('CHANNELS_FILE_PATH'):
            raise NotConfigured('CHANNELS_FILE_PATH is not configured properly')
        if not self.settings.get('PACKAGES_FILE_PATH'):
            raise NotConfigured('PACKAGES_FILE_PATH is not configured properly')
        if not self.settings.get('COMPETITOR_NAME'):
            raise NotConfigured('COMPETITOR_NAME is not configured properly')
        if not self.settings.get('FILTER_KEYWORDS_FILE_PATH'):
            raise NotConfigured('FILTER_KEYWORDS_FILE_PATH is not configured properly')
        if not self.settings.get('FILTER_CHANNELS_FILE_PATH'):
            raise NotConfigured('FILTER_CHANNELS_FILE_PATH is not configured properly')
        self.CHANNELS_CACHE = {}
        self.FEED_KEYWORDS = csv_to_records(settings.get('FEED_KEYWORDS_FILE_PATH'), 'utf-8-sig')
        with open(settings.get('FILTER_CHANNELS_FILE_PATH'), encoding='utf-8') as f:
            self.FILTER_CHANNELS = set([x.strip().lower() for x in f.read().splitlines()])
        with open(settings.get('FILTER_KEYWORDS_FILE_PATH'), encoding='utf-8') as f:
            self.KEYWORDS = set([x.strip().lower() for x in f.read().splitlines()])
        self.CHANNELS_DF = pd.read_csv(settings.get('CHANNELS_FILE_PATH'), encoding='utf-8', dtype=str)
        self.CHANNELS_DF = self.CHANNELS_DF.replace(np.nan, '')
        self.CHANNELS_DF = self.CHANNELS_DF.replace('nan', '')

        self.COMPETITOR_NAME = settings.get('COMPETITOR_NAME')
        self.PACKAGE_NAMES = {
            x['Package Name']: x['Telogical Package Name']
            for x in csv_to_records(settings.get('PACKAGES_FILE_PATH'), encoding='utf-8-sig')
            if x['Competitor'] == self.COMPETITOR_NAME
        }
        # Vectorized normalization for performance
        self.vfunc_nnm = np.vectorize(normalize_and_match)
        self.runtype = spider.runtype.lower()
        if self.runtype == 'discovery':
            logger.info('Running CLUs as a Discovery run')
        else:
            logger.info('Running CLUs as a Full run')

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings, crawler.spider)
        return pipeline

    def process_item(self, item, spider):
        if self.runtype == 'discovery':
            if self.isdiscovery(item['Channel Name']):
                return self.do_process(item)
        else:
            return self.do_process(item)

        raise DropItem('Item is filtered out by Discovery Parameters')

    def do_process(self, item):
        telogical_meta = self.CHANNELS_CACHE.get(item['Channel Name'])
        if not isinstance(telogical_meta, dict):
           telogical_meta = self.cross_reference(item['Channel Name'])

        item['Telogical Name'] = telogical_meta['Telogical Name']

        if isinstance(item.get('Resolution'), type(None)):
            item['Resolution'] = telogical_meta['Resolution']

        item['Package Name'] = self.PACKAGE_NAMES.get(item['Package Name'], item['Package Name'])
        item['Feed'] = telogical_meta['Feed']
        item['DEW?'] = telogical_meta['DEW?']
        item['Channel Genre'] = telogical_meta['Channel Genre']
        item['LineupType'] = '<N/A>'

        return item

    def cross_reference(self, channel):
        try:
            telogical_meta: dict = self.CHANNELS_DF.loc[
                self.vfunc_nnm(self.CHANNELS_DF['Channel Name'].values, channel)
            ].reset_index(drop=True).iloc[0]
        except IndexError:
            telogical_meta = {column_name: '<N/A>' for column_name in self.CHANNELS_DF.columns}

        resolution, feed = self.resolution_and_feed(telogical_meta['Telogical Name'])
        resolution2, feed2 = self.resolution_and_feed(channel)

        if feed == '<N/A>':
            feed = feed2
        if resolution == '<N/A>':
            resolution = resolution2

        telogical_meta['Resolution'] = resolution
        telogical_meta['Feed'] = feed
        telogical_meta['DEW?'] = 'NO' if telogical_meta['Not to be put in DEW'] == 'TRUE' else ''

        self.CHANNELS_CACHE[channel] = telogical_meta

        return telogical_meta

    def resolution_and_feed(self, channel):
        channel = channel.lower()

        res = ["".join(x) for x in re.findall(r'\b(hd)\b|\b(sd)\b', channel)]
        if any(res):
            resolution = res[0].upper()
        else:
            resolution = '<N/A>'

        for feed in self.FEED_KEYWORDS:
            find_feed = ["".join(x) for x in re.findall(feed['Regex'], channel)]
            if any(find_feed):
                feed_val = feed['Feed']
                return resolution, feed_val

        feed_val = '<N/A>'

        return resolution, feed_val

    def isdiscovery(self, channel: str) -> bool:
        channel = channel.strip().lower()

        if channel in self.FILTER_CHANNELS:
            return True

        for word in self.KEYWORDS:
            expression = '.*{}.*'.format(word)
            if re.match(expression, channel):
                return True

        return False
