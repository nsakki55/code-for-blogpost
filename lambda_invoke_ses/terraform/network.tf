resource "aws_vpc" "main" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  availability_zone = "${var.aws_region}a"
  cidr_block        = "10.1.10.0/24"
}

locals {
  aws_services = [
    "com.amazonaws.${var.aws_region}.email-smtp",
    "com.amazonaws.${var.aws_region}.secretsmanager",
  ]
}

resource "aws_vpc_endpoint" "aws_services_interface_type" {
  for_each            = toset(local.aws_services)
  vpc_id              = aws_vpc.main.id
  service_name        = each.value
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = [aws_subnet.private.id]
  security_group_ids  = [aws_security_group.aws_services_interface_endpoints.id]
  tags = {
    Name = "Invoke SES via SMTP"
  }
}

resource "aws_security_group" "aws_services_interface_endpoints" {
  name   = "aws-services-interface-endpoints-sg"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "invoke_ses" {
  name   = "invoke-ses-sg"
  vpc_id = aws_vpc.main.id
}

resource "aws_vpc_security_group_egress_rule" "invoke_ses" {
  security_group_id = aws_security_group.invoke_ses.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  from_port         = -1
  to_port           = -1
}

resource "aws_vpc_security_group_ingress_rule" "allows_access_to_interface_endpoints" {
  security_group_id            = aws_security_group.aws_services_interface_endpoints.id
  referenced_security_group_id = aws_security_group.invoke_ses.id
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allows_smtp_access_to_interface_endpoints" {
  security_group_id            = aws_security_group.aws_services_interface_endpoints.id
  referenced_security_group_id = aws_security_group.invoke_ses.id
  from_port                    = 587
  to_port                      = 587
  ip_protocol                  = "tcp"
}
