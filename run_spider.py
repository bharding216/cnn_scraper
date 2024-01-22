from scrapy.crawler import CrawlerProcess
from cnn_scraper.spiders.cnn_spider import CnnSpider 

def run_spider():
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'FEEDS': {
            'cnn_articles.json': {
                'format': 'json',
                'overwrite': True, 
            },
        },
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    })

    process.crawl(CnnSpider)
    process.start()

if __name__ == "__main__":
    run_spider()
