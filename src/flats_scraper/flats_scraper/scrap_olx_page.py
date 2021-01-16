from flats_scraper.scraper_model import Link, Advertisement, User
import re
from datetime import datetime
import requests
from lxml import html
from sqlalchemy import and_, or_


def parse_olx_time(dt_string):
    str_to_month = {"stycznia": 1,
                    "lutego": 2,
                    "marca": 3,
                    "kwietnia": 4,
                    "maja": 5,
                    "czerwca": 6,
                    "lipca": 7,
                    "sierpnia": 8,
                    "września": 9,
                    "października": 10,
                    "listopada": 11,
                    "grudnia": 12}
    hour, minute, day, month, year = re.findall(
        r".*(\d{1,2}):(\d{1,2}).\s(\d{1,2})\s(\w+)\s(\d{4})", dt_string)[0]
    return datetime(
        int(year),
        str_to_month[month],
        int(day),
        hour=int(hour),
        minute=int(minute))


def get_number_from_string(string):
    return float("".join(re.findall(r'(\d*,?\d+)', string)).replace(",", "."))


def parse_mmm_yyyy(string):
    str_to_month = {"sty": 1,
                    "lut": 2,
                    "mar": 3,
                    "kwi": 4,
                    "maj": 5,
                    "cze": 6,
                    "lip": 7,
                    "sie": 8,
                    "wrz": 9,
                    "paź": 10,
                    "lis": 11,
                    "gru": 12}
    month, year = re.findall(r'(\w+)\s(\d{4})', string)[0]
    return datetime(int(year), str_to_month[month], 1, 0, 0, 0)


def scrap_olx_ad(html_link):
    page = requests.get(html_link)
    tree = html.fromstring(page.content)
    print(f"trying {html_link}")
    if page.status_code != 200:
        raise Exception("Wrong return code")
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
        return None

    table_keys = tree.xpath(
        "//ul[@class='offer-details']/li/a/span//text()")
    table_values = tree.xpath(
        "//ul[@class='offer-details']/li/a/strong//text()")
    table_keys2 = tree.xpath(
        "//ul[@class='offer-details']/li/span/span//text()")
    table_values2 = tree.xpath(
        "//ul[@class='offer-details']/li/span/strong//text()")
    table_parsed = {}
    values = table_values + table_values2
    for i, key in enumerate(table_keys + table_keys2):

        if key_new := fields_mapping.get(key):
            table_parsed[key_new] = values[i]
        else:
            table_parsed[key] = values[i]
    description = " ".join(tree.xpath("//div[@id='textContent']//text()"))
    price = tree.xpath(
        "//strong[contains(@class, 'pricelabel__value')]//text()")[0]
    views_number = tree.xpath(
        "//*[contains(@class, " +
        "'offer-bottombar__counter')]/strong//text()")[0]
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
        floor = int(table_parsed.get('floor'))
    if table_parsed.get('furniture') == "Tak":
        furniture = 'yes'
    else:
        furniture = 'no'

    olx_id = tree.xpath(
        "//*[contains(@class, 'offer-bottombar__item')]/strong//text()")[0]
    added_time = parse_olx_time(tree.xpath(
        "//*[contains(@class, 'offer-bottombar__item')]/em/strong//text()"
    )[0])
    title = tree.xpath(
        "//div[@class='offer-titlebox']/h1//text()")[0].strip()
    username = "".join(tree.xpath(
        '//div[@class="offer-user__actions"]/h4//text()')).strip()
    since = re.findall(r'(\w{3}\s\d{4})', tree.xpath(
        "//span[@class='user-since']/text()")[0])[0]
    on_olx_since = parse_mmm_yyyy(since)
    user_href_assigned = tree.xpath('//a[@class="user-offers"]')
    user_slug = 'No href available for user'
    if user_href_assigned:
        user_slug = user_href_assigned[0].attrib.get('href')

    user_data = dict(
        username=username,
        olx_user_slug=user_slug,
        on_olx_since=on_olx_since)
    advertisement_data = dict(
        title=title,
        description=description,
        scraped_time=datetime.now(),
        private_business=advertiser_type,
        floor=floor,
        builttype=table_parsed.get('builttype'),
        room_no=table_parsed.get('room_no'),
        furniture=furniture,
        price=get_number_from_string(price),
        size_m2=get_number_from_string(table_parsed.get('size_m2')),
        location=location,
        latitude=lat,
        longitude=lon,
        olx_id=olx_id,
        added_time=added_time,
        views_number=views_number)
    return advertisement_data, user_data


def mass_scrap_olx(db_sqlalchemy_session, limit_to_scrap):
    ads = db_sqlalchemy_session.query(Link).\
        filter(Link.is_closed.isnot(1)).\
        filter(Link.link_type.is_('olx')).\
        order_by(Link.last_time_scraped).\
        limit(limit_to_scrap).\
        all()
    objects_for_commit = []
    for link in ads:
        html_link = link.url
        link_id = link.id
        scrap_result = scrap_olx_ad(html_link)
        if scrap_result:
            advertisement_data, user_data = scrap_result

            user = db_sqlalchemy_session.query(User).filter(
                or_(
                    and_(User.username.is_(user_data['username']),
                         User.on_olx_since.is_(user_data['on_olx_since'])),
                    User.olx_user_slug.is_(user_data['olx_user_slug'])
                )).first()
            if not user:
                user = User(**user_data)
            advertisement = Advertisement(
                **advertisement_data, user=user, link_id=link_id)
            link = db_sqlalchemy_session.query(Link).get(link_id)
            link.last_time_scraped = datetime.now()
            objects_for_commit.extend((link, advertisement))
        else:
            link = db_sqlalchemy_session.query(Link).get(link_id)
            link.is_closed = True
            objects_for_commit.append(link)
    db_sqlalchemy_session.add_all(objects_for_commit)
    db_sqlalchemy_session.commit()
