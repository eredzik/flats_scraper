from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawlers.spiders.olx_otodom import OlxOtodomSpider
from pathlib import Path
import time
import os


def run_scraper(timestr):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    output = 'scraped/scraped_' + timestr + '.json'
    Path("scraped").mkdir(parents=True, exist_ok=True)
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawlers.settings'
    settings = get_project_settings()
    settings['FEED_FORMAT'] = 'json'
    settings['FEED_URI'] = output
    print(settings.attributes['USER_AGENT'])
    process = CrawlerProcess(settings)
    process.crawl(OlxOtodomSpider)
    process.start()
    return(output)
