from prefect import flow, task, get_run_logger
import pandas as pd
import boto3

s3_client = boto3.Session().client("s3")
S3_BUCKET = "prefect-etl-tutorial"


@task(name="extract task")
def extract(file_name: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"download {file_name} from s3")

    s3_client.download_file(S3_BUCKET, file_name, file_name)
    df = pd.read_csv(file_name)
    return df


@task(name="transform task")
def transform(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("transform extract dataset")

    df_transformed = df.groupby(["type1"])["weight_kg"].mean().reset_index()
    return df_transformed


@task(name="load task")
def load(df: pd.DataFrame, file_name: str) -> None:
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
