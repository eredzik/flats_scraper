import json
import re
import traceback
from datetime import datetime, timedelta

import requests
from lxml import html
from prefect import Flow, Parameter, task
import prefect
from prefect.engine.executors.dask import LocalDaskExecutor
from prefect.engine.signals import SKIP
from prefect.tasks.control_flow.conditional import switch
from prefect.utilities.debug import raise_on_exception
from sqlalchemy import and_, create_engine, desc, or_
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from flats_scraper import scraper_settings
from flats_scraper.scraper_model import Advertisement, Link, User


def parse_olx_time(dt_string):
    str_to_month = {"stycznia": 1, "lutego": 2, "marca":3, "kwietnia":4, "maja":5, "czerwca":6, "lipca":7, "sierpnia": 8, "września":9, "października":10, "listopada":11, "grudnia": 12}
    hour, minute, day, month, year = re.findall(r".*(\d{1,2}):(\d{1,2}).\s(\d{1,2})\s(\w+)\s(\d{4})", dt_string)[0]
    return datetime(int(year), str_to_month[month], int(day), hour = int(hour), minute = int(minute))

@task()
def get_to_parse(limit, _):
    engine = create_engine(scraper_settings.db_uri)
    session = Session(bind=engine)
    logger = prefect.context.get("logger")

    ads = session.query(Link).\
        filter(Link.is_closed.isnot(True)).\
        order_by(Link.last_time_scraped).\
        limit(limit).\
        all()
    result = {"olx":[], "otodom":[]}
    for ad in ads:
        if ad.link_type == 'olx':
            result['olx'].append((ad.url, ad.id))
        elif ad.link_type == 'otodom':
            result['otodom'].append((ad.url, ad.id))
        else:
            logger.inf
    session.close()
    return result

def get_number_from_string(string):
    return float("".join(re.findall(r'(\d*,?\d+)',string)).replace(",", "."))

def parse_mmm_yyyy(string):
    str_to_month = {"sty": 1, "lut": 2, "mar":3, "kwi":4, "maj":5, "cze":6, "lip":7, "sie": 8, "wrz":9, "paź":10, "lis":11, "gru": 12}
    month, year = re.findall(r'(\w+)\s(\d{4})', string)[0]
    return datetime(int(year), str_to_month[month], 1,0,0,0)

@task(max_retries=3, retry_delay = timedelta(seconds=5))
def scrap_olx_ad(ad):
    html_link, link_id = ad
    engine = create_engine(scraper_settings.db_uri)
    session = Session(bind=engine)
    page = requests.get(html_link)
    tree = html.fromstring(page.content)
    try:
        print(f"trying {html_link}")
        fields_mapping = {"Oferta od": "private_business", 
                        "Poziom": "floor",
                        "Rynek": "market", 
                        "Rodzaj zabudowy": "builttype",
                        "Liczba pokoi": "room_no",
                        "Umeblowane": "furniture",
                        "Powierzchnia": "size_m2"}
        
        if tree.xpath('//*[@id="offer_removed_by_user"]') or \
            tree.xpath('//*[@id="offer_outdated"]') or \
            tree.xpath('//*[@id="ad-not-available-box"]'):
            link = session.query(Link).get(link_id)
            link.is_closed = True
            session.commit()
            session.close()
            return

        table_keys = tree.xpath("//ul[@class='offer-details']/li/a/span//text()")
        table_values = tree.xpath("//ul[@class='offer-details']/li/a/strong//text()")
        table_keys2 = tree.xpath("//ul[@class='offer-details']/li/span/span//text()")
        table_values2 = tree.xpath("//ul[@class='offer-details']/li/span/strong//text()")
        table_parsed = {}
        values = table_values + table_values2
        for i, key in enumerate(table_keys + table_keys2):
        
            if key_new := fields_mapping.get(key):
                table_parsed[key_new] = values[i]
            else:
                table_parsed[key] = values[i]
        description = " ".join(tree.xpath("//div[@id='textContent']//text()"))
        price = tree.xpath("//strong[contains(@class, 'pricelabel__value')]//text()")[0]
        views_number = tree.xpath("//*[contains(@class, 'offer-bottombar__counter')]/strong//text()")[0]
        location = tree.xpath("//address/p//text()")[0]
        lat_lon = tree.xpath("//div[@id='mapcontainer']")[0].attrib
        lon = lat_lon['data-lon']
        lat = lat_lon['data-lat']

        if table_parsed.get('private_business') == "Biuro / Deweloper":
            advertiser_type = "business"
        else:
            advertiser_type = "private"
        if table_parsed.get('floor') == "Parter":
            floor = 0
        elif table_parsed.get('floor') == "Powyżej 10":
            floor = 11
        else:
            floor = table_parsed.get('floor')
        if table_parsed.get('furniture') == "Tak":
            furniture = 'yes'
        else:
            furniture = 'no'


        olx_id = tree.xpath("//*[contains(@class, 'offer-bottombar__item')]/strong//text()")[0]
        added_time = parse_olx_time(tree.xpath("//*[contains(@class, 'offer-bottombar__item')]/em/strong//text()")[0])
        title = tree.xpath("//div[@class='offer-titlebox']/h1//text()")[0].strip()
        username = "".join(tree.xpath('//div[@class="offer-user__actions"]/h4//text()')).strip()
        since = re.findall(r'(\w{3}\s\d{4})',tree.xpath("//span[@class='user-since']/text()")[0])[0]
        on_olx_since = parse_mmm_yyyy(since)
        user_href_assigned = tree.xpath('//a[@class="user-offers"]')
        user = None
        user_slug = 'No href available for user'
        if user_href_assigned:
            user_slug = user_href_assigned[0].attrib.get('href')
            user = session.query(User).filter(
                or_(
                    and_(User.username.is_(username),User.on_olx_since.is_(on_olx_since)),
                    User.olx_user_slug.is_(user_slug)
                )).first()
        if not user:
            user = User(username = username,
                        olx_user_slug = user_slug,
                        on_olx_since = on_olx_since)
        
        advertisement = Advertisement(
            title = title,
            link_id = link_id,
            description = description,
            scraped_time = datetime.now(),
            private_business = advertiser_type,
            floor = floor,
            builttype = table_parsed.get('builttype'),
            room_no = table_parsed.get('room_no'),
            furniture = furniture,
            price = get_number_from_string(price),
            size_m2 = get_number_from_string(table_parsed.get('size_m2')),
            location = location,
            latitude = lat,
            longitude = lon,
            olx_id = olx_id,
            added_time = added_time,
            views_number = views_number,
            user = user,
        )
        session.add(advertisement)
        link = session.query(Link).get(link_id)
        link.last_time_scraped = datetime.now()
        session.commit()
        session.close()
        return
    except:
        with open(f"exceptions/dump_{link_id}.html", "wb") as f:
            f.write(page.content)
        with open(f"exceptions/log_error{link_id}.log", 'w') as log:
            traceback.print_exc(file=log)

@task(max_retries=3, retry_delay = timedelta(seconds=5))
def scrap_otodom_ad(ad):
    html_link, link_id = ad
    engine = create_engine(scraper_settings.db_uri)
    session = Session(bind=engine)
    logger = prefect.context.get("logger")
    print(f"trying {html_link}")
    page = requests.get(html_link)
    
    if page.status_code != 200:
        raise Exception("Wrong return code")
    try:
        tree = html.fromstring(page.content)
        if tree.xpath("//div[@id='ad-not-available-box']"):
            link = session.query(Link).get(link_id)
            link.is_closed = True
            logger.info("Closing ad - not available anymore")
            session.commit()
            return

        json_content = json.loads(tree.xpath('//*[@id="server-app-state"]/text()')[0])
        
        meta_content = json_content['initialProps']['meta']['target']
        data_content = json_content['initialProps']['data']['advert']

        # Ad data
        if floor_content := meta_content.get('Floor_no'):
            if floor_content[0] == 'ground_floor':
                floor_no = 0
            elif floor_content[0] == 'cellar':
                floor_no = -1
            elif floor_content[0] == 'floor_higher_10':
                floor_no = 11
            elif floor_content[0] == 'garret':
                floor_no = 20
            else:
                floor_no = re.findall(r'\d+', floor_content[0])[0]
        else:
            floor_no = None
        equipment = meta_content.get('Equipment_types') or []
        if 'furniture' in equipment:
            furniture = 'yes'
        else:
            furniture = 'no'

        if meta_content.get('Building_type'):
            building_type = meta_content.get('Building_type')[0]
        else:
            building_type = None
        
        if build_year := meta_content.get('Build_year'):
            build_year = int(build_year)

        # User data
        username = data_content.get('advertOwner').get("name")
        user_phone = data_content.get('advertOwner').get("phones")[0]
        agency_name, agency_adress, agency_otodom_id = (None, None, None)
        if agency_data := data_content.get('agency'):
            agency_name = agency_data.get('name')
            agency_adress = agency_data.get('address')
            agency_otodom_id = agency_data.get("id")
        
        # User DB row
        user = session.\
            query(User).\
            filter(User.phone_number.is_(user_phone), User.username.is_(user_phone)).\
            first()
        if not user:
            user = User(
                username = username,
                agency_name = agency_name,
                agency_otodom_id = agency_otodom_id,
                agency_address = agency_adress,
                phone_number = user_phone
            )
        # Ad DB row
        advertisement = Advertisement(
            link_id = link_id,
            scraped_time = datetime.now(),
            title = data_content['title'],
            description = data_content['description'],
            private_business = data_content['advertiser_type'],
            floor = floor_no,
            builttype = building_type,
            room_no = int(meta_content['Rooms_num'][0]),
            furniture = furniture,
            price = float(meta_content['Price']),
            size_m2 = float(meta_content['Area']),
            build_year = build_year,
            location = data_content['location']['address'],
            latitude = data_content['location']['coordinates']['latitude'],
            longitude =  data_content['location']['coordinates']['longitude'],
            otodom_id = meta_content['Id'],
            added_time = datetime.strptime(data_content['dateCreated'], '%Y-%m-%d %H:%M:%S'),
            user = user
        )
        session.add(advertisement)
        link = session.query(Link).get(link_id)
        link.last_time_scraped = datetime.now()
        session.commit()
        session.close()
        logger.info("Ad scraped successfully")
    except:
        with open(f"exceptions/dump_{link_id}.html", "wb") as f:
            f.write(page.content)
        with open(f"exceptions/log_error{link_id}.log", 'w') as log:
            traceback.print_exc(file=log)
