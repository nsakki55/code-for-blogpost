ECR_REPOSITORY := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
DOCKER_TAG := latest
DOCKER_IMAGE := invoke-ses

build:
	docker build -t $(ECR_REPOSITORY)/$(DOCKER_IMAGE):$(DOCKER_TAG) . \
	  --build-arg FROM_ADDRESS=$(FROM_ADDRESS) \
	  --build-arg TO_ADDRESS=$(TO_ADDRESS)

push:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_IMAGE):$(DOCKER_TAG)
