variable "access_key" {
}

variable "secret_key" {
}

variable "region" {
}

variable "prefect_api_key" {
}

variable "prefect_api_url" {
}

provider "aws" {
  version    = "3.37.0"
  access_key = var.access_key
  secret_key = var.secret_key
  region     = var.region
}
