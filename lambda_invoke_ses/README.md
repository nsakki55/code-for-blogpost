# Invoke SES via VPC Endpoint from lambda function in private subnet
## Setup Environment Variable
Please set the following environment variables before deploying the infrastructure.
- AWS_ACCOUNT_ID: target aws account for creating resources by terraform
- AWS_REGION: target aws region for deploying lambda and ses resources
- DOMAIN: domain name for creating ses domain identity
- FROM_ADDRESS: from email address for email set by lambda
- TO_ADDRESS: to email address for email set by lambda
```
$ export AWS_ACCOUNT_ID=<aws_account_id> 
$ export AWS_REGION=<aws_region>
$ export DOMAIN=<domain>
$ export FROM_ADDRESS=<from_address>
$ export TO_ADDRESS=<to_address>
```

## Deploy AWS Resources 
```
$ cd terraform
$ terraform init
$ terraform apply -var="aws_account_id=$AWS_ACCOUNT_ID" -var="aws_region=$AWS_REGION" -var="domain=$DOMAIN" 
```

## Deploy Lambda Function
```
$ make build
$ make push
```
