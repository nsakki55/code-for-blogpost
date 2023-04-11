FROM prefecthq/prefect:2.8.7-python3.8

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY my_flow.py /opt/prefect/flows/my_flow.py