from datetime import datetime

import requests
from lxml import html
from prefect import Flow, Parameter, task, context
from prefect.utilities.debug import raise_on_exception

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import scraper_settings
from scraper_model import Link


@task 
def get_ads(pages_to_scrap, page_to_scrap = None):
    ads = []
    page_to_scrap = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/'
    for _ in range(pages_to_scrap):
        page = requests.get(page_to_scrap)
        ads_xpath = "//a[contains(@class,'marginright5 link linkWithHash detailsLink')]"
        tree = html.fromstring(page.content)
        for ad in tree.xpath(ads_xpath):
            ads.append(ad.attrib['href'])
        next_site_xpath = "//a[@data-cy='page-link-next']"
        page_to_scrap = tree.xpath(next_site_xpath)[0].attrib['href']

    return ads

@task
def add_link_to_db(link):
    engine = create_engine(scraper_settings.db_uri)
    session = Session(bind=engine)
    logger = context.get("logger")

    if not session.query(Link).filter(Link.url == link).first():
        logger.info(f"Adding link {link} to database")
        if link.find("otodom.pl") > 0:
            link_type = 'otodom'
        elif link.find("olx.pl") > 0:
            link_type = 'olx'
        else:
            link_type = 'other'
        
        link = Link(url = link,
                    first_time_seen = datetime.now(),
                    link_type = link_type)
        session.add(link)
        session.commit()
    else:
        logger.info(f"Ignored link {link} - exists")

with Flow("Scrap_for_urls") as flow:
    pages_to_scrap = Parameter("pages_to_scrap", default=1)
    ads = get_ads(pages_to_scrap)
    add_link_to_db.map(ads) 

if __name__ == '__main__':
    flow.visualize()
    with raise_on_exception():
        state = flow.run(pages_to_scrap=5)
    flow.visualize(flow_state = state)
