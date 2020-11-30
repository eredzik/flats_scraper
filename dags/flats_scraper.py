
from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
from sqlalchemy.orm import sessionmaker

from flats_scraper.get_links import get_ads

with DAG("get_links") as dag:
    pg_engine = PostgresHook(
        postgres_conn_id="", schema="").get_sqlalchemy_engine()
    session = sessionmaker(bind=pg_engine)()
    PythonOperator(task_id="get_links_task",
                   python_callable=get_ads, op_args=[session, 25])
