import json
import csv
from json import JSONDecodeError
import time
from run_scraping import run_scraper

timestr = time.strftime("%Y%m%d-%H%M%S")
csv_name = 'scraped/scraped_'+timestr+'.csv'


def process_to_csv(json_file, csv_file):
    with open(json_file, 'rb') as f:
        try:
            json_crawled = json.loads(f.read())
        except JSONDecodeError:
            print("Nothing scraped, check scraper")
            return

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
