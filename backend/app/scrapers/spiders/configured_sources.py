"""Public portal discovery example and inactive notice spider template."""
import scrapy

class DataGovPortalCatalogSpider(scrapy.Spider):
    name="datagov_portal_catalog"
    allowed_domains=["data.gov.in"]
    start_urls=["https://data.gov.in/"]
    def parse(self,response):
        for href in response.css("a::attr(href)").getall():
            url=response.urljoin(href)
            if "data.gov.in" in url:
                yield scrapy.Request(url,callback=self.parse_public_page)
    def parse_public_page(self,response):
        title=response.css("h1::text").get() or response.css("title::text").get()
        if title:
            yield {"source_name":"data.gov.in portal discovery","source_url":response.url,
                   "title":" ".join(title.split()),"page_type":"public_portal_page"}

class ExamplePublicNoticeSpider(scrapy.Spider):
    """Inactive template. Configure an actual approved source before use."""
    name="example_public_notices"
    allowed_domains=["example.gov.in"]
    start_urls=[]
    def parse(self,response):
        for row in response.css("article, .notice, .view-content .views-row"):
            title=row.css("h2 a::text, h3 a::text, a::text").get()
            href=row.css("h2 a::attr(href), h3 a::attr(href), a::attr(href)").get()
            if title and href:
                yield {"source_name":self.name,"source_url":response.urljoin(href),"title":" ".join(title.split())}
        next_page=response.css("a[rel=next]::attr(href), li.pager__item--next a::attr(href)").get()
        if next_page: yield response.follow(next_page,callback=self.parse)
