import scrapy
from unidecode import unidecode
import re
from cnn_scraper.items import CnnScraperItem

class CnnSpider(scrapy.Spider):
    name = 'cnn'
    allowed_domains = ['cnn.com']
    start_urls = ['https://www.cnn.com/world']

    def parse(self, response):
        # Extract the links to the main articles from the 'world news' page.
        main_article_links = response.css('a.container__link--type-article::attr(href)').getall()

        # Follow the links to the main articles and parse each article's content.
        for link in main_article_links:
            if not link.startswith('https://www.cnn.com'):
                link = 'https://www.cnn.com' + link
            yield scrapy.Request(url=link, callback=self.parse_article)

        # Follow pagination links (if applicable).
        next_page = response.css('a.pagination__next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_article(self, response):
        # Extract the title, date, author, and content of the article.
        item = CnnScraperItem()

        raw_title = response.css('h1.headline__text::text').get(default='').strip()
        normalized_title = unidecode(raw_title)
        item['title'] = normalized_title
        
        raw_date = response.css('div.timestamp::text').get(default='').strip() \
                .replace('Updated', '').replace('Published', '').replace('\n', '').replace('  ', ' ')
        date_match = re.search(r'\b(\w+ \d+, \d{4})\b', raw_date)
        if date_match:
            item['date'] = date_match.group(1)
        else:
            item['date'] = ''
          
        def extract_author(response, css_selector, regex_pattern):
            text = response.css(css_selector).get(default='')
            match = re.search(regex_pattern, text)
            return match.group(1) if match else text

        css_selectors = ['div.byline__names span.byline__name::text', 'div.byline__names::text']
        regex_pattern = r'\s*By\s+(.*),\s+CNN'

        for css_selector in css_selectors:
            item['author'] = extract_author(response, css_selector, regex_pattern)
            if item['author']:
                break

        item['content'] = response.css('div.article__content div p::text').getall()
        item['link'] = response.url
        yield item