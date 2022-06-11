FROM 354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3

RUN pip3 install --upgrade pip
RUN pip3 install optuna==2.10.0

ADD extend_sagemaker_container/extend_sagemaker_container_trainig_script.py /opt/ml/code/extend_sagemaker_container_trainig_script.py

# Defines train.py as script entrypoint
ENV SAGEMAKER_PROGRAM extend_sagemaker_container_trainig_script.py
