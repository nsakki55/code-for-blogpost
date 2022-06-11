FROM python:3.6-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++

RUN pip3 install pandas numpy joblib scikit-learn cython
RUN pip3 install fastFM

ADD scratch_container/scratch_container_training_script.py scratch_container_training_script.py

WORKDIR /

ENTRYPOINT ["python", "scratch_container_training_script.py"]