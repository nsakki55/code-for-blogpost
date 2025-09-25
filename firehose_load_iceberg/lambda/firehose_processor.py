import base64
import json


def lambda_handler(firehose_records_input, context):
    print(
        "Received records for processing from DeliveryStream: "
        + firehose_records_input["deliveryStreamArn"]
    )

    firehose_records_output = {}
    firehose_records_output["records"] = []

    for firehose_record_input in firehose_records_input["records"]:
        payload_bytes = base64.b64decode(firehose_record_input["data"]).decode("utf-8")
        payload_dict = json.loads(payload_bytes)

        converted_data_dict = {}
        destination_table_name = None

        # 共通イベントデータ
        event_type = payload_dict["eventType"]
        converted_data_dict["event_type"] = event_type
        converted_data_dict["message_id"] = payload_dict["mail"]["messageId"]
        converted_data_dict["tags"] = payload_dict["mail"]["tags"]
        headers = payload_dict["mail"]["headers"]
        for header in headers:
            match header["name"]:
                case "From":
                    converted_data_dict["from_address"] = header["value"]
                case "To":
                    converted_data_dict["to_address"] = header["value"]

        # Sendイベントデータ用処理
        if event_type == "Send":
            converted_data_dict["timestamp"] = payload_dict["mail"]["timestamp"]
            destination_table_name = "send_log"

        # Openイベントデータ用処理
        if event_type == "Open":
            converted_data_dict["ip_address"] = payload_dict["open"]["ipAddress"]
            converted_data_dict["user_agent"] = payload_dict["open"]["userAgent"]
            converted_data_dict["timestamp"] = payload_dict["open"]["timestamp"]
            destination_table_name = "open_log"

        # Clickイベントデータ用処理
        if event_type == "Click":
            converted_data_dict["ip_address"] = payload_dict["click"]["ipAddress"]
            converted_data_dict["link"] = payload_dict["click"]["link"]
            converted_data_dict["link_tags"] = payload_dict["click"]["linkTags"]
            converted_data_dict["user_agent"] = payload_dict["click"]["userAgent"]
            converted_data_dict["timestamp"] = payload_dict["click"]["timestamp"]
            destination_table_name = "click_log"

        converted_data_str = json.dumps(converted_data_dict)
        print("converted_data_str:", converted_data_str)

        # イベントごとに送信先テーブルを指定
        firehose_record_output = {}
        firehose_record_output["data"] = base64.b64encode(
            converted_data_str.encode("utf-8")
        )
        firehose_record_output["recordId"] = firehose_record_input["recordId"]
        firehose_record_output["result"] = "Ok"
        firehose_record_output["metadata"] = {
            "otfMetadata": {
                "destinationDatabaseName": "email_event",
                "destinationTableName": destination_table_name,
                "operation": "insert",
            }
        }
        firehose_records_output["records"].append(firehose_record_output)
        print(firehose_record_output)

    return firehose_records_output
