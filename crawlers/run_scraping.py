from scrapy.cmdline import execute
import os
import time


def run_scraper():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    output = 'scraped/scraped_' + timestr + '.json'
    try:
        os.mkdir("scraped")
        os.remove(output)

    except OSError:
        pass
    execute(['scrapy', 'crawl', 'olx_otodom', '-o', output])
