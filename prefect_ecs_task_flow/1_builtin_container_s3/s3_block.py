from prefect.filesystems import S3
import os

block = S3(bucket_path="prefect-etl",
           aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
           aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)
block.save("etl-s3-block", overwrite=True)
