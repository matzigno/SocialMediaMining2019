# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class InstagramnetItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field()
    destination = scrapy.Field()
