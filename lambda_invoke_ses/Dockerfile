FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

ARG FROM_ADDRESS
ARG TO_ADDRESS
ENV FROM_ADDRESS=${FROM_ADDRESS}
ENV TO_ADDRESS=${TO_ADDRESS}

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY lambda_function/invoke_ses.py ${LAMBDA_TASK_ROOT}

CMD ["invoke_ses.handler"]
