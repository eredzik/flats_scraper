import re
from datetime import datetime

import requests
from lxml import html
from flats_scraper.scraper_model import Link


def get_ads(pages_to_scrap,
            page_to_scrap='https://www.olx.pl' +
            '/nieruchomosci/mieszkania/sprzedaz/warszawa/'):
    ads = []
    for i in range(pages_to_scrap):
        try:
            page = requests.get(page_to_scrap)
            ads_xpath = r"//a[contains(@class," + \
                r"'marginright5 link linkWithHash detailsLink')]"
            tree = html.fromstring(page.content)
            for ad in tree.xpath(ads_xpath):
                ad_clean = re.findall(r'(.*\.html).*', ad.attrib['href'])[0]
                ads.append(ad_clean)
            next_site_xpath = "//a[@data-cy='page-link-next']"
            try:
                page_to_scrap = tree.xpath(next_site_xpath)[0].attrib['href']
            except IndexError:
                pass
        except (ValueError, IndexError):
            raise ValueError(
                f"Unable to scrap data from {page_to_scrap} which is page {i}")

    return ads


def add_link_to_db(session, ads):
    to_add = []
    for html_path in set(ads):
        if not session.query(Link).filter(Link.url == html_path).first():
            if html_path.find("otodom.pl") > 0:
                link_type = 'otodom'
            elif html_path.find("olx.pl") > 0:
                link_type = 'olx'
            else:
                link_type = 'other'

            link = Link(url=html_path,
                        first_time_seen=datetime.now(),
                        link_type=link_type)
            to_add.append(link)
    session.bulk_save_objects(to_add, return_defaults=True)
    session.commit()


def get_links_db(session, number_of_pages):
    ads = get_ads(number_of_pages)
    add_link_to_db(session, ads)
