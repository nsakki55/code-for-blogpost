FROM 354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3

ADD extend_sagemaker_container/trainer.py /opt/ml/code/trainer.py

# Defines train.py as script entrypoint
# https://github.com/aws/sagemaker-training-toolkit#create-a-docker-image-and-train-a-model
ENV SAGEMAKER_PROGRAM trainer.py
