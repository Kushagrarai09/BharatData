from scrapy.http import HtmlResponse, Request
from app.scrapers.spiders.base import ConfigurablePublicSpider

def test_configurable_spider_extracts_records_and_pagination():
    config = {
        "name": "sample",
        "allowed_domains": ["example.gov.in"],
        "start_urls": ["https://example.gov.in/notices"],
        "selectors": {
            "container": "div.notice",
            "title": "h2 a::text",
            "date": "time::attr(datetime)",
            "category": ".category::text",
            "document": "a.pdf::attr(href)",
            "next": "a.next::attr(href)",
        },
    }
    spider = ConfigurablePublicSpider(config=__import__("json").dumps(config))
    html = b"""
    <div class='notice'><h2><a>Test public notice</a></h2><time datetime='2026-11-25'></time>
    <span class='category'>Recruitment</span><a class='pdf' href='/docs/notice.pdf'>PDF</a></div>
    <a class='next' href='/notices?page=2'>Next</a>
    """
    request = Request("https://example.gov.in/notices")
    response = HtmlResponse(request.url, request=request, body=html, encoding="utf-8")
    results = list(spider.parse(response))
    item = results[0]
    assert item["title"] == "Test public notice"
    assert item["document_url"] == "https://example.gov.in/docs/notice.pdf"
    assert results[1].url == "https://example.gov.in/notices?page=2"
