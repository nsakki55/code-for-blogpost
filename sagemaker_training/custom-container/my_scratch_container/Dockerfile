FROM python:3.6-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++

RUN pip3 install pandas numpy joblib scikit-learn cython
RUN pip3 install fastFM

ADD my_scratch_container/trainer.py ./trainer.py

WORKDIR /

ENTRYPOINT ["python", "trainer.py"]