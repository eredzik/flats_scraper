# import alembic
import pytest
import sqlalchemy
from flats_scraper.get_links import get_links_db
from flats_scraper.scrap_olx_page import mass_scrap_olx
from flats_scraper.scrap_otodom_page import mass_scrap_otodom
from flats_scraper.scraper_model import Advertisement, Link, User
from sqlalchemy import func

# def migrate_in_memory(migrations_path,
# alembic_ini_path=None, connection=None, revision="head"):
#     config = alembic.config.Config(alembic_ini_path)
#     config.set_main_option('script_location', migrations_path)
#     config.set_main_option('sqlalchemy.url', 'sqlite:///:memory:')
#     if connection is not None:
#         config.attributes['connection'] = connection
#     alembic.command.upgrade(config, revision)


@pytest.mark.dependency()
def test_mass_ads_scraping(session):
    get_links_db(session, 2)
    assert session.query(Link.id).count() > 0


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


@pytest.mark.dependency(depends=['test_mass_ads_scraping'])
def test_mass_olx_scraping(session):
    mass_scrap_olx(session, 50)

    assert get_count(session.query(Link).join(
        Advertisement, Link.id == Advertisement.link_id)) > 0


@ pytest.mark.dependency(depends=['test_mass_ads_scraping'])
def test_mass_otodom_scraping(session):
    mass_scrap_otodom(session, 50)

    assert session.query(Link).filter(Link.link_type == "otodom").count() > 0
    assert session.query(Link).join(
        Advertisement, Link.id == Advertisement.link_id).count() > 0
    assert session.query(User.id).count() > 0
