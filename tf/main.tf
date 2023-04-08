terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "1.45.1"
    }
  }
}

# AK, SK and Region configured in terraform.tfvars
variable "hwcloud_region" { type = string }
variable "hwcloud_ak" { type = string }
variable "hwcloud_sk" { type = string }

provider "huaweicloud" {
  region     = var.hwcloud_region
  access_key = var.hwcloud_ak
  secret_key = var.hwcloud_sk
}

locals {
  all_ipv4        = "0.0.0.0/0"
  all_ipv6        = "::/0"
}
