resource "aws_route53_zone" "ses_smtp" {
  name = var.domain
}

resource "aws_ses_configuration_set" "ses_smtp" {
  name = "ses-smtp-config-set"
}

resource "aws_ses_domain_identity" "ses_smtp" {
  domain = aws_route53_zone.ses_smtp.name
}

resource "aws_route53_record" "txt_ses_smtp" {
  zone_id = aws_route53_zone.ses_smtp.zone_id
  name    = "_amazonses.${aws_route53_zone.ses_smtp.name}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.ses_smtp.verification_token]
}

# DKIM
resource "aws_ses_domain_dkim" "ses_smtp" {
  domain = aws_route53_zone.ses_smtp.name
  depends_on = [
    aws_ses_domain_identity.ses_smtp
  ]
}

resource "aws_route53_record" "cname_dkim_ses_smtp" {
  count   = 3
  zone_id = aws_route53_zone.ses_smtp.zone_id
  name    = "${element(aws_ses_domain_dkim.ses_smtp.dkim_tokens, count.index)}._domainkey.${aws_route53_zone.ses_smtp.name}"
  type    = "CNAME"
  ttl     = "600"
  records = ["${element(aws_ses_domain_dkim.ses_smtp.dkim_tokens, count.index)}.dkim.amazonses.com"]
}

# SPF
resource "aws_ses_domain_mail_from" "ses_smtp" {
  domain           = aws_route53_zone.ses_smtp.name
  mail_from_domain = "mail.${aws_route53_zone.ses_smtp.name}"
  depends_on = [
    aws_ses_domain_identity.ses_smtp
  ]
}

resource "aws_route53_record" "mx_mail_ses_smtp" {
  zone_id = aws_route53_zone.ses_smtp.zone_id
  name    = aws_ses_domain_mail_from.ses_smtp.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.${var.aws_region}.amazonses.com"]
}

resource "aws_route53_record" "txt_mail_ses_smtp_domain" {
  zone_id = aws_route53_zone.ses_smtp.zone_id
  name    = aws_ses_domain_mail_from.ses_smtp.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com ~all"]
}

# DMARC
resource "aws_route53_record" "txt_dmarc_ses_smtp" {
  zone_id = aws_route53_zone.ses_smtp.zone_id
  name    = "_dmarc.${aws_route53_zone.ses_smtp.name}"
  type    = "TXT"
  ttl     = "600"
  records = ["v=DMARC1;p=quarantine;pct=25;rua=mailto:dmarcreports@${aws_route53_zone.ses_smtp.name}"]
}

resource "aws_iam_user" "smtp_user" {
  name = "smtp-user"
}

resource "aws_iam_access_key" "smtp_user_key" {
  user = aws_iam_user.smtp_user.name
}

resource "aws_secretsmanager_secret" "smtp_credential" {
  name = "smtp-credential"
}

resource "aws_secretsmanager_secret_version" "smtp_credentials" {
 secret_id = aws_secretsmanager_secret.smtp_credential.id
 secret_string = jsonencode({
   username = aws_iam_access_key.smtp_user_key.id
   password = aws_iam_access_key.smtp_user_key.ses_smtp_password_v4
 })
}

resource "aws_iam_user_policy" "smtp_user_policy" {
  name = "smtp-user-policy"
  user = aws_iam_user.smtp_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}