CREATE TABLE email_event.send_log (
    event_type string,
    message_id string,
    from_address string,
    to_address string,
    timestamp timestamp,
    tags string
) LOCATION 's3://glue-data-20250924084554937700000001/email_event/send_log/' TBLPROPERTIES (
    'table_type' = 'ICEBERG',
    'format' = 'parquet',
    'write_compression' = 'gzip'
);