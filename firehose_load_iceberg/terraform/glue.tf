resource "aws_s3_bucket" "glue_data" {
  bucket_prefix = "glue-data-"
}

resource "aws_glue_catalog_database" "email_event" {
  name         = "email_event"
  location_uri = "s3a://${aws_s3_bucket.glue_data.bucket}/email_event/"
}
