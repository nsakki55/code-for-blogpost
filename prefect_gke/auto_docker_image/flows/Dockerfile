FROM prefecthq/prefect:2.13.7-python3.8
COPY requirements.txt /opt/prefect/requirements.txt
RUN python -m pip install -r /opt/prefect/requirements.txt
COPY . /opt/prefect/flows/
COPY . /opt/prefect/
WORKDIR /opt/prefect/
