"""HTML extraction template for a publicly accessible mandi-price listing page.

Prefer the official data.gov.in resource API for the canonical dataset. Use this spider
only for a separate public HTML listing whose terms permit crawling.
"""
import scrapy

class MandiHtmlListingSpider(scrapy.Spider):
    name = "mandi_html_listing"
    allowed_domains = ["example.gov.in"]
    start_urls = []

    def parse(self, response):
        for row in response.css("table tbody tr"):
            cells = [ " ".join(" ".join(cell.css("::text").getall()).split())
                      for cell in row.css("td") ]
            if len(cells) >= 4:
                yield {
                    "source_name": self.name,
                    "source_url": response.url,
                    "market": cells[0],
                    "commodity": cells[1],
                    "arrival_date": cells[2],
                    "modal_price": cells[3],
                }
        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
