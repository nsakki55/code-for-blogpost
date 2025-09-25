import json

import boto3

DELIVERY_STREAM_NAME = "firehose-load-iceberg"
JSON_FILE_PATH = "event_data/open.json"


def main():
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    firehose_client = boto3.client("firehose", region_name="ap-northeast-1")
    response = firehose_client.put_record(
        DeliveryStreamName=DELIVERY_STREAM_NAME,
        Record={"Data": json.dumps(data, ensure_ascii=False).encode("utf-8")},
    )
    print(f"send data to firehose success: RecordId={response['RecordId']}")


if __name__ == "__main__":
    main()
