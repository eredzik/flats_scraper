from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawlers.spiders.olx_otodom import OlxOtodomSpider
import os
import time


def run_scraper(timestr):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    output = 'scraped/scraped_' + timestr + '.json'
    try:
        os.mkdir("scraped")
        os.remove(output)

    except OSError:
        pass
    settings = get_project_settings()
    settings['FEED_FORMAT'] = 'json'
    settings['FEED_URI'] = output
    process = CrawlerProcess(settings)
    process.crawl(OlxOtodomSpider)
    process.start()
    return(output)

