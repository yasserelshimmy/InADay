# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from datetime import date
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from rpath_utils.xlsxexporter import XlsxItemExporter
from scrapy.exceptions import NotConfigured


class DefaultPipeline(object):

    def __init__(self, settings, spider):
        self.settings = settings
        if not self.settings.get('OUTPUT_FILE_DIR'):
            raise NotConfigured('OUTPUT_FILE_DIR not configured properly')

        self.BOT_NAME = self.settings.get('BOT_NAME')
        self.sheet_name = self.settings.get(
            'SHEET_NAME',
            self.BOT_NAME
        )

        self.filepath = self.gen_output_file_name()
        spider.OUTPUT_FILE_PATH = self.filepath
        self.file = open(self.filepath, 'w+b')
        if self.settings.get('STREAM_TO_EXCEL', True):
            self.exporter = XlsxItemExporter(file=self.file, sheet_name=self.sheet_name)
        else:
            self.exporter = CsvItemExporter(file=self.file)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings, crawler.spider)
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        if self.settings.get('FIELDS_TO_EXPORT', False):
            self.exporter.fields_to_export = self.settings.get('FIELDS_TO_EXPORT')
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def gen_output_file_name(self):
        today = date.today().strftime("%m-%d-%Y")
        OUTPUT_FILE_DIR = self.settings.get('OUTPUT_FILE_DIR')

        if self.settings.get('STREAM_TO_EXCEL', True):
            file_extension = 'xlsx'
        else:
            file_extension = 'csv'

        increment = 0
        while os.path.exists(
                os.path.join(OUTPUT_FILE_DIR, f"{self.BOT_NAME}_{today}_{increment}.{file_extension}")):
            increment += 1

        return os.path.join(OUTPUT_FILE_DIR, f"{self.BOT_NAME}_{today}_{increment}.{file_extension}")
