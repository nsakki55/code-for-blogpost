# Glue Job Test using LocalStack
## SetUp docker container 
```zsh
$ docker compose up -d
```
## Run Glue Job accessing Localstack S3 bucket 
### Access to Glue Dev container 
```zsh
$ docker compose exec glue.dev bash
```

### Create S3 bucket in Localstack
```zsh
$ aws s3 mb s3://test-job-bucket --endpoint-url http://s3.dev:4566
```
### Copy sample data to S3 bucket in Localstack
```zsh
$ aws s3 mv ./data/test_data.csv s3://test-job-bucket/test_data.csv --endpoint-url http://s3.dev:4566
```
### Run Glue Job locally
```zsh
$ python3 glue_job.py --JOB_NAME test
```

### List objects in S3 bucket in Localstack
```zsh
$ aws s3api list-objects-v2 --bucket test-job-bucket  --endpoint-url http://s3.dev:4566
```

## Test Glue Job Code
```zsh
$ docker compose exec -T -u glue_user -w /home/glue_user/workspace glue.dev /home/glue_user/.local/bin/pytest
```

or run test in docker container directly
```zsh
$ docker compose exec glue.dev bash
$ pytest
```