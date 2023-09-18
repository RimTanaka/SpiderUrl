from scrapy.crawler import CrawlerProcess
from Get_Url_Task.Get_Url_Tz.spiders.test_task import TestTaskSpider


def start_spider():
    process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.1234.56 Safari/537.36',
    })

    process.crawl(TestTaskSpider)
    process.start()

if __name__ == '__main__':
    start_spider()

