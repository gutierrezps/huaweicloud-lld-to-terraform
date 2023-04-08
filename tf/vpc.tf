resource "huaweicloud_vpc" "dev" {
  region  = "sa-brazil-1"
  name    = "DEV"
  cidr    = "10.1.0.0/12"
  description = "Development"
}

resource "huaweicloud_vpc" "stg" {
  region  = "sa-brazil-1"
  name    = "STG"
  cidr    = "10.2.0.0/12"
  description = "Staging"
}

resource "huaweicloud_vpc" "prod" {
  region  = "sa-brazil-1"
  name    = "PROD"
  cidr    = "10.3.0.0/12"
  description = "Production"
}

resource "huaweicloud_vpc" "net" {
  region  = "sa-brazil-1"
  name    = "NET"
  cidr    = "10.4.0.0/24"
  description = "Inter-network"
}

