
# from datetime import datetime, timedelta

# from airflow import DAG
# from airflow.hooks.postgres_hook import PostgresHook
# from airflow.operators.python_operator import PythonOperator
# from sqlalchemy.orm import sessionmaker

# from flats_scraper.get_links import get_links_db

# with DAG("get_links",
#          schedule_interval=timedelta(minutes=5),
#          start_date=datetime(2020, 1, 1)) as dag:
#     pg_engine = PostgresHook(
#         postgres_conn_id="SCRAPER_DB", schema="").get_sqlalchemy_engine()
#     session = sessionmaker(bind=pg_engine)()
#     PythonOperator(task_id="get_links_task",
#                    python_callable=get_links_db, op_args=[session, 25])
