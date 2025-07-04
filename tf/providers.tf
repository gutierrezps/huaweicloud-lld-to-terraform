terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.76.1"
    }
  }
}

provider "huaweicloud" {
  region     = var.region
  access_key = var.hwc_access_key
  secret_key = var.hwc_secret_key
}
