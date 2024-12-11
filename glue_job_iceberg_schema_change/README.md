# Change schema for iceberg table in AWS Glue Job
Sample repository to change schema automatically for iceberg table in AWS Glue Job.

## Requirements
- python 3.12
- terraform 1.9.7

## Setup
Create aws resource for glue job
```bash
$ cd terraform
$ terraform init
$ terraform apply
```

Upload sample data to S3 bucket.  
Please change the bucket name created by terraform in your environment.
```bash
$ aws s3 cp ./data/test_data.csv s3://schema-change-data-20241208085330834400000002/input/
$ aws s3 cp ./data/test_data_new_column.csv s3://schema-change-data-20241208085330834400000002/input/
```

Upload script to S3 bucket.   
Please change the bucket name created by terraform in your environment.
```bash
$ aws s3 cp ./src/update_iceberg_table_schema.py s3://glue-job-20241208085330834300000001/scripts/ 
```

## Run Glue Job
```bash
$ aws glue start-job-run \
    --job-name update_iceberg_table_schema \
    --arguments '{"--file_name": "test_data.csv"}'
```

## Reference
- https://iceberg.apache.org/docs/1.5.0/spark-writes/#schema-merge