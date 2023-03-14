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

resource "huaweicloud_vpc" "vpc_prod" {
  name = "vpc-prod"
  cidr = "10.1.0.0/16"
}

resource "huaweicloud_vpc_subnet" "subnet_prod_1" {
  name        = "subnet-prod-1"
  cidr        = "10.1.1.0/24"
  gateway_ip  = "10.1.1.1"
  vpc_id      = huaweicloud_vpc.vpc_prod.id
  availability_zone = "sa-brazil-1b"
}

resource "huaweicloud_vpc_subnet" "subnet_prod_2" {
  name        = "subnet-prod-2"
  cidr        = "10.1.2.0/24"
  gateway_ip  = "10.1.2.1"
  vpc_id      = huaweicloud_vpc.vpc_prod.id
  availability_zone = "sa-brazil-1b"
}

resource "huaweicloud_vpc" "vpc_sync" {
  name = "vpc-sync"
  cidr = "10.2.0.0/16"
}

resource "huaweicloud_vpc_subnet" "subnet_sync_1" {
  name        = "subnet-sync-1"
  cidr        = "10.2.1.0/24"
  gateway_ip  = "10.2.1.1"
  vpc_id      = huaweicloud_vpc.vpc_sync.id
  availability_zone = "sa-brazil-1b"
}


resource "huaweicloud_vpc_subnet" "subnet_sync_2" {
  name        = "subnet-sync-2"
  cidr        = "10.2.2.0/24"
  gateway_ip  = "10.2.2.1"
  vpc_id      = huaweicloud_vpc.vpc_sync.id
  availability_zone = "sa-brazil-1b"
}

resource "huaweicloud_networking_secgroup" "sg_prod" {
  name        = "sg-prod"
}

resource "huaweicloud_networking_secgroup" "sg_test" {
  name        = "sg-test"
}
