from sqlalchemy.orm import sessionmaker
from flats_scraper.scraper_model import Base
from sqlalchemy import create_engine
import pytest


@pytest.fixture(scope="session")
def session():
    engine = create_engine('sqlite:///db.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
