echo 'Failed connecting to postgres' | nc -w 60 airflow-backend 5432; echo $?

pip3 install /root/airflow/src/

airflow initdb
sleep 1
airflow connections --add --conn_id 'SCRAPER_DB' --conn_uri "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@mydb:5432/${POSTGRES_DB}" &\
airflow scheduler & \
airflow webserver & \
wait