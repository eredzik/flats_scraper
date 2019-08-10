import json
import csv
from scrapy.cmdline import execute
import os
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
json_name = 'scraped/scraped_'+timestr+'.json'
# json_name = 'scraped/scraped_20190806-195334.json'
csv_name = 'scraped/scraped_'+timestr+'.csv'


def run_scraper(output):
    try:
        os.remove(output)
    except OSError:
        pass
    execute(['scrapy', 'crawl', 'olx_otodom', '-o', output])


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


run_scraper(json_name)
process_to_csv(json_name, csv_name)
