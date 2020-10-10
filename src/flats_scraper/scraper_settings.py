import os

from dotenv import find_dotenv, load_dotenv
import prefect

load_dotenv(find_dotenv())
postgres_user = os.environ.get("POSTGRES_USER") or prefect.context.secrets['POSTGRES_USER']
postgres_password = os.environ.get("POSTGRES_PASSWORD") or prefect.context.secrets['POSTGRES_PASSWORD']
db_uri = f"postgresql://{postgres_user}:{postgres_password}@localhost:5433/flats_scraper_db"
