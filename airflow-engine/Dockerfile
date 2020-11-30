# Airflow seems to crash with Python 3.8, it's important to use version 3.7 instead
FROM python:3.7

# Install and setup Airflow
RUN pip3 install 'apache-airflow[postgres,crypto]'

# Configure Airflow: connect to backend
WORKDIR /root/airflow/
COPY airflow.cfg airflow.cfg
COPY main.sh main.sh
RUN chmod 700 airflow.cfg
RUN chmod +x main.sh
CMD ./main.sh