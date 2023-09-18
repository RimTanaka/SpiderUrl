# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyItem(scrapy.Item):
    Title = scrapy.Field(default='н/д')
    Description = scrapy.Field(default='н/д')
    Email = scrapy.Field(default='н/д')
    Phone = scrapy.Field(default='н/д')
    Address = scrapy.Field(default='н/д')
    Inn = scrapy.Field(default='н/д')
    Ogrn = scrapy.Field(default='н/д')
