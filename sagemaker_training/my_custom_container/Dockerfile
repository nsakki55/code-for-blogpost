FROM python:3.6-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++

RUN pip3 install pandas numpy joblib scikit-learn cython
RUN pip3 install fastFM
RUN pip3 install sagemaker-training


# ADD train /opt/ml/code/train
ADD my_custom_container/trainer.py /opt/ml/code/trainer.py

# Defines train.py as script entrypoint
# https://github.com/aws/sagemaker-training-toolkit#create-a-docker-image-and-train-a-model
ENV SAGEMAKER_PROGRAM trainer.py