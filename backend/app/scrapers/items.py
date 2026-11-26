import scrapy

class BharatDataItem(scrapy.Item):
    source_name = scrapy.Field()
    source_url = scrapy.Field()
    title = scrapy.Field()
    published_date = scrapy.Field()
    category = scrapy.Field()
    document_url = scrapy.Field()
    raw_fields = scrapy.Field()
