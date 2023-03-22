from prefect import flow, task, get_run_logger
import pandas as pd
from prefect_aws import AwsCredentials

aws_credentials_block = AwsCredentials.load("default")
s3_client = aws_credentials_block.get_boto3_session().client("s3")

S3_BUCKET = "prefect-etl-tutorial"


@task(name="extract task")
def extract(file_name: str) -> pd.DataFrame:
    """
    Download an object from S3 bucket.

    Args:
        file_name: Name of bucket download file name.
    Returns:
        download file with dataframe format.
    """
    logger = get_run_logger()
    logger.info(f"download {file_name} from s3")

    s3_client.download_file(S3_BUCKET, file_name, file_name)
    df = pd.read_csv(file_name)
    return df


@task(name="transform task")
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform extract dataframe.

    Args:
        df: dataframe downloaded from s3
    Returns:
        transformed dataset
    """
    logger = get_run_logger()
    logger.info("transform extract dataset")

    df_transformed = df.groupby(["type1"]).mean().reset_index()
    return df_transformed


@task(name="load task")
def load(df: pd.DataFrame, file_name: str) -> None:
    """
    Upload an object to S3 bucket.

    Args:
        df: upload dataframe object.
        file_name: Name of bucket download file name.
    """

    logger = get_run_logger()
    logger.info(f"upload {file_name} to s3")

    df.to_csv(file_name)
    s3_client.upload_file(file_name, S3_BUCKET, file_name)


@flow(name="ETL Flow")
def etl_flow(download_file_name: str, upload_file_name: str):
    logger = get_run_logger()
    logger.info("ETL flow start")

    extracted_df = extract(file_name=download_file_name)
    transformed_df = transform(extracted_df)
    load(transformed_df, file_name=upload_file_name)

    logger.info("ETL flow finished")


if __name__ == "__main__":
    etl_flow(download_file_name="pokemon.csv", upload_file_name="pokemon_transformed.csv")
