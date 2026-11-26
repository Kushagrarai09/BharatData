"""Config-driven spider with pagination and CSS selectors."""
import json
from urllib.parse import urljoin
import scrapy
from app.scrapers.items import BharatDataItem

class ConfigurablePublicSpider(scrapy.Spider):
    name = "configurable_public"
    allowed_domains = []
    start_urls = []
    source_name = "public_source"
    selectors = {
        "container": "article",
        "title": "h2 a::text",
        "date": "time::attr(datetime)",
        "category": ".category::text",
        "document": "a[href$='.pdf']::attr(href)",
        "next": "a[rel='next']::attr(href)",
    }

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if config:
            cfg = json.loads(config) if isinstance(config, str) else config
            self.source_name = cfg.get("name", self.source_name)
            self.start_urls = cfg.get("start_urls", self.start_urls)
            self.allowed_domains = cfg.get("allowed_domains", self.allowed_domains)
            self.selectors = {**self.selectors, **cfg.get("selectors", {})}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers={"Accept": "text/html"})

    def parse(self, response):
        for node in response.css(self.selectors["container"]):
            title = node.css(self.selectors["title"]).get()
            if not title and self.selectors["title"].startswith("//"):
                title = node.xpath(self.selectors["title"]).get()
            if not title:
                continue
            pdf = node.css(self.selectors["document"]).get()
            yield BharatDataItem(
                source_name=self.source_name,
                source_url=response.url,
                title=" ".join(title.split()),
                published_date=node.css(self.selectors["date"]).get(),
                category=node.css(self.selectors["category"]).get(),
                document_url=urljoin(response.url, pdf) if pdf else None,
                raw_fields={"html_snippet": node.get()[:4000]},
            )
        next_url = response.css(self.selectors["next"]).get()
        if next_url:
            yield response.follow(next_url, callback=self.parse)
