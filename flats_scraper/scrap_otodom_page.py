from datetime import datetime
import json
import re
from flats_scraper.scraper_model import Link, Advertisement, User
import requests
from lxml import html


def scrap_otodom_ad(html_link):
    print(f"trying {html_link}")
    page = requests.get(html_link)

    if page.status_code != 200:
        raise Exception("Wrong return code")
    tree = html.fromstring(page.content)
    if tree.xpath("//div[@id='ad-not-available-box']"):
        return None

    json_content = json.loads(tree.xpath(
        '//*[@id="server-app-state"]/text()')[0])

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
            floor_no = int(re.findall(r'\d+', floor_content[0])[0])
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
    advertisement_data = dict(
        scraped_time=datetime.now(),
        title=data_content['title'],
        description=data_content['description'],
        private_business=data_content['advertiser_type'],
        floor=floor_no,
        builttype=building_type,
        room_no=int(meta_content['Rooms_num'][0]),
        furniture=furniture,
        price=float(meta_content['Price']),
        size_m2=float(meta_content['Area']),
        build_year=build_year,
        location=data_content['location']['address'],
        latitude=data_content['location']['coordinates']['latitude'],
        longitude=data_content['location']['coordinates']['longitude'],
        otodom_id=meta_content['Id'],
        added_time=datetime.strptime(
            data_content['dateCreated'], '%Y-%m-%d %H:%M:%S'))
    user_data = dict(
        username=username,
        agency_name=agency_name,
        agency_otodom_id=agency_otodom_id,
        agency_address=agency_adress,
        phone_number=user_phone)
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
