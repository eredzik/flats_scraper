from datetime import datetime
import re

import requests
from lxml import html
from prefect import Flow, Parameter, task, context
from prefect.utilities.debug import raise_on_exception
from prefect.engine.executors.dask import LocalDaskExecutor


from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import flats_scraper.scraper_settings
from flats_scraper.scraper_model import Link


@task 
def get_ads(pages_to_scrap, page_to_scrap = None):
    ads = []
    page_to_scrap = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/'
    for _ in range(pages_to_scrap):
        try:
            page = requests.get(page_to_scrap)
            ads_xpath = "//a[contains(@class,'marginright5 link linkWithHash detailsLink')]"
            tree = html.fromstring(page.content)
            for ad in tree.xpath(ads_xpath):
                ad_clean = re.findall(r'(.*\.html).*',ad.attrib['href'])[0]
                ads.append(ad_clean)
            next_site_xpath = "//a[@data-cy='page-link-next']"
            page_to_scrap = tree.xpath(next_site_xpath)[0].attrib['href']
        except:
            with open("exceptions/dump.html", "wb") as f:
                f.write(page.content)
        

    return ads

@task
def add_link_to_db(links):
    engine = create_engine(flats_scraper.scraper_settings.db_uri)
    session = Session(bind=engine)
    logger = context.get("logger")
    to_add = []
    for html in set(links):
        if not session.query(Link).filter(Link.url == html).first():
            logger.info(f"Adding link {html} to database")
            if html.find("otodom.pl") > 0:
                link_type = 'otodom'
            elif html.find("olx.pl") > 0:
                link_type = 'olx'
            else:
                link_type = 'other'
            
            link = Link(url = html,
                        first_time_seen = datetime.now(),
                        link_type = link_type)
            to_add.append(link)
            
        else:
            logger.info(f"Ignored link {html} - exists")
    session.bulk_save_objects(to_add)
    session.commit()
    session.close()

with Flow("Scrap_for_urls") as flow_get_links:
    pages_to_scrap = Parameter("pages_to_scrap", default=1)
    ads = get_ads(pages_to_scrap)
    add_link_to_db(ads) 

if __name__ == '__main__':
    executor = LocalDaskExecutor()
    state = flow_get_links.run(executor=executor, pages_to_scrap=15)
