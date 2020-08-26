from sqlalchemy import MetaData, Integer, String, Unicode, Column, Float, DateTime, ForeignKey, Boolean, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
metadata = MetaData()
Base = declarative_base(metadata=metadata)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    olx_user_slug = Column(String(100))
    on_olx_since = Column(DateTime)
    phone_number = Column(String(20))
    agency_otodom_id = Column(Integer)
    agency_name = Column(String(100))
    agency_address = Column(String(100))

class Advertisement(Base):
    __tablename__ = 'advertisement'
    id = Column(Integer, primary_key = True, autoincrement=True)
    link_id = Column(Integer,  ForeignKey('link.id'))
    scraped_time = Column(DateTime)
    title = Column(String(100), nullable = False)
    description = Column(Unicode(5000))
    private_business = Column(String(30))
    floor = Column(Integer)
    builttype = Column(String)
    room_no = Column(Integer)
    furniture = Column(String)
    price = Column(Float(10), nullable = False)
    size_m2 = Column(Float, nullable = False)
    build_year = Column(Integer)
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    olx_id = Column(Integer)
    otodom_id = Column(Integer)
    added_time = Column(DateTime)
    views_number = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref = "user")

class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False) 
    first_time_seen = Column(DateTime, nullable=False)
    last_time_scraped = Column(DateTime)
    is_closed = Column(Boolean)
    link_type = Column(String(10), nullable=False)
    advertisement = relationship("Advertisement", backref="advertisements")

    uq_url = UniqueConstraint(url)