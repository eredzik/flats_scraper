from datetime import datetime, timedelta

from prefect import Flow, Parameter
from prefect.engine.executors.dask import LocalDaskExecutor
from prefect.schedules import IntervalSchedule
from prefect.tasks.prefect import FlowRunTask

from flats_scraper.get_links import add_link_to_db, get_ads
from flats_scraper.scraping_schedule import get_to_parse, scrap_olx_ad, scrap_otodom_ad

schedule = IntervalSchedule(
    start_date=datetime.utcnow() + timedelta(seconds=1),
    interval=timedelta(minutes=30),
)

with Flow("data_processing_flow", schedule=schedule) as main_flow:
    pages_to_scrap = Parameter("pages_to_scrap", default=24)
    ads = get_ads(pages_to_scrap)
    added_links_rc = add_link_to_db(ads) 

    limit = Parameter("limit", default=400)
    
    ads = get_to_parse(limit, added_links_rc)
    results_olx = scrap_olx_ad.map(ads['olx'])
    results_otodom = scrap_otodom_ad.map(ads['otodom'])
    # main_flow.run(executor=LocalDaskExecutor())
main_flow.register("Flats scraper flow project")

