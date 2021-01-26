import json
import re
from datetime import datetime

import requests
from lxml import html

from flats_scraper.parse_functions import get_number_from_string
from flats_scraper.scraper_model import Advertisement, Link, User


def scrap_otodom_ad(html_link):
    print(f"trying {html_link}")
    page = requests.get(html_link)

    if page.status_code != 200:
        raise Exception("Wrong return code")
    tree = html.fromstring(page.content)
    if tree.xpath("//div[@id='ad-not-available-box']"):
        return None
    # ad_data =
    # size_m2 = tree.xpath("//div[@aria-label='Powierzchnia']/div[2]")[0]
    # title = tree.xpath("//h1[@data-cy='adPageAdTitle']")[0]
    # description = tree.xpath("//div[@data-cy='adPageAdDescription']")
    # private_business = tree.xpath("//aside/div/div/div")
    # floor_no = int(tree.xpath("//div[@aria-label='Piętro']/div")[1].text)
    # builttype = tree.xpath("//div[@aria-label='Rodzaj zabudowy']/div")
    # room_no = tree.xpath("//div[@aria-label='Liczba pokoi']/div")
    # furniture = None
    # price = get_number_from_string(tree.xpath(
    #     "//strong[@aria-label='Cena']")[0].text)
    # build_year = tree.xpath("//div[@aria-label='Rok budowy']/div")
    # location = tree.xpath("//a[@href='#map']")
    # otodom_id = tree.xpath("//div[contains(text(), 'Nr oferty')]")
    # added_time = tree.xpath("//div[contains(text(), 'Data dodania')]")
    added_time = None
    # username = tree.xpath("//span[contains(@class, 'contactPersonName')]")
    # agency_name = None
    # agency_otodom_id = None
    # agency_adress = None
    # phone_number = None

    json_content = json.loads(tree.xpath(
        "//script[@id='__NEXT_DATA__']")[0].text)

    latitude = json_content['props']['pageProps']['adTrackingData']['lat']
    longitude = json_content['props']['pageProps']['adTrackingData']['long']
    title = json_content['props']['pageProps']['ad']['title']
    otodom_id = json_content['props']['pageProps']['ad']['id']
    description = json_content['props']['pageProps']['ad']['description']
    private_business = json_content['props']['pageProps']['ad']['advertiserType']
    floor = json_content['props']['pageProps']['ad']['target'].get('Floor_no')
    if floor:
        if floor[0] == 'ground_floor':
            floor = 0
        else:
            floor = get_number_from_string(floor[0])

    builttype = json_content['props']['pageProps']['ad']['target'].get(
        'Building_type')
    if builttype:
        builttype = builttype[0]
    room_no = json_content['props']['pageProps']['ad']['target']['Rooms_num'][0]
    furniture = None
    price = json_content['props']['pageProps']['ad']['target']['Price']
    size_m2 = json_content['props']['pageProps']['ad']['target']['Area']
    build_year = json_content['props']['pageProps']['ad']['target'].get(
        'Build_year')
    if build_year:
        build_year = int(build_year)
    location = json_content['props']['pageProps']['ad']['location']['address'][0]['value']
    username = json_content['props']['pageProps']['ad']['owner']['name']
    agency = json_content['props']['pageProps']['ad']['agency']
    if agency:
        agency_name = agency.get("name")
        agency_otodom_id = agency.get("id")
    else:
        agency_name = None
        agency_otodom_id = None
    phone_number = json_content['props']['pageProps']['ad']['owner']['phones'][0]
    agency_adress = None
    # added_time = None
    advertisement_data = dict(
        scraped_time=datetime.now(),
        title=title,
        description=description,
        private_business=private_business,
        floor=floor,
        builttype=builttype,
        room_no=room_no,
        furniture=furniture,
        price=price,
        size_m2=size_m2,
        build_year=build_year,
        location=location,
        latitude=latitude,
        longitude=longitude,
        otodom_id=otodom_id,
        added_time=added_time)
    user_data = dict(
        username=username,
        agency_name=agency_name,
        agency_otodom_id=agency_otodom_id,
        agency_address=agency_adress,
        phone_number=phone_number)
    return advertisement_data, user_data


def mass_scrap_otodom(db_sqlalchemy_session, limit_to_scrap):
    ads = db_sqlalchemy_session.query(Link).\
        filter(Link.is_closed.isnot(1)).\
        filter(Link.link_type.is_('otodom')).\
        order_by(Link.last_time_scraped).\
        limit(limit_to_scrap).\
        all()
    objects_for_commit = []
    # session.commit()
    for link in ads:
        html_link = link.url
        link_id = link.id
        scraping_results = scrap_otodom_ad(html_link)
        link = db_sqlalchemy_session.query(Link).get(link_id)
        if scraping_results:
            advertisement_data, user_data = scraping_results
            user = db_sqlalchemy_session.\
                query(User).\
                filter(User.phone_number.is_(user_data['phone_number']),
                       User.username.is_(user_data['username'])).\
                first()
            if not user:
                user = User(**user_data)
            advertisement = Advertisement(**advertisement_data, user=user)
            link.last_time_scraped = datetime.now()
            objects_for_commit.extend((advertisement, user, link))
        else:
            link.is_closed = True
            objects_for_commit.append(link)
    db_sqlalchemy_session.add_all(objects_for_commit)
    db_sqlalchemy_session.commit()
