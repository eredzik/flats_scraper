
import os
import time
import json
import csv
import time

# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from crawlers.crawlers.spiders.olx_otodom import OlxOtodomSpider

timestr = time.strftime("%Y%m%d-%H%M%S")
csv_name = 'scraped/scraped_'+timestr+'.csv'


def run_scraper(timestr):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    output = 'D:\\flats_scraper\\flats_scraper\\scraped\\scraped_' + timestr + '.json'
    os.makedirs("scraped", exist_ok=True)
    # settings = get_project_settings()
    # settings['FEED_FORMAT'] = 'json'
    # settings['FEED_URI'] = output
    # process = CrawlerProcess(settings)
    # process.crawl(OlxOtodomSpider)
    # process.start()
    os.chdir("D:\\\\\\flats_scraper\\flats_scraper\\crawlers\\crawlers")
    print(output)
    os.system("scrapy crawl olx_otodom -o {0}".format(output))
    return(output)


def process_to_csv(json_file, csv_file):
    with open(json_file, 'rb') as f:
        json_crawled = json.loads(f.read())

    unique_keys = set()
    for ad in json_crawled:
        for key in ad.keys():
            unique_keys.add(key)
    unique_keys = list(unique_keys)
    print(unique_keys)

    with open(csv_file, "w", encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(unique_keys)
        for ad in json_crawled:
            to_save = [ad.get(x, '') for x in unique_keys]
            print(to_save)
            writer.writerow(to_save)


json_name = run_scraper(timestr)
process_to_csv(json_name, csv_name)
