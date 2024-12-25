import os
import json
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_smtp_credential() -> tuple[str, str]:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name="ap-northeast-1")
    response = client.get_secret_value(SecretId="smtp-credential")
    secret = json.loads(response["SecretString"])

    smtp_username = secret["username"]
    smtp_password = secret["password"]
    return smtp_username, smtp_password


def handler(event, context) -> None:
    # メールの作成
    msg = MIMEMultipart()
    msg["From"] = os.environ['FROM_ADDRESS']
    msg["To"] = os.environ['TO_ADDRESS']
    msg["Subject"] = "test title"
    email_body = "This is test email via smtp."
    msg.attach(MIMEText(email_body, "plain"))

    # SMTPサーバーにメール送信
    smtp_server = "email-smtp.ap-northeast-1.amazonaws.com"
    smtp_port = 587
    smtp_username, smtp_password = get_smtp_credential()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    return {"statusCode": 200, "body": json.dumps("Email sent successfully")}
