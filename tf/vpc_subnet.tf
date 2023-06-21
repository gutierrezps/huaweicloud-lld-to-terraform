resource "huaweicloud_vpc" "dev" {
  region  = "sa-brazil-1"
  name    = "DEV"
  cidr    = "10.1.0.0/16"
  description = "Development"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id
}

resource "huaweicloud_vpc" "stg" {
  region  = "sa-brazil-1"
  name    = "STG"
  cidr    = "10.2.0.0/16"
  description = "Staging"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_stg.id
}

resource "huaweicloud_vpc" "prod" {
  region  = "sa-brazil-1"
  name    = "PROD"
  cidr    = "10.3.0.0/16"
  description = "Production"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id
}

resource "huaweicloud_vpc" "net" {
  region  = "sa-brazil-1"
  name    = "NET"
  cidr    = "10.4.0.0/16"
  description = "Inter-network"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_net.id
}

resource "huaweicloud_vpc_subnet" "dev_dev01" {
  region      = huaweicloud_vpc.dev.region
  name        = "DEV01"
  cidr        = "10.1.1.0/24"
  gateway_ip  = "10.1.1.1"
  vpc_id      = huaweicloud_vpc.dev.id
  description = "Development-01"
  availability_zone = "sa-brazil-1b"
}

resource "huaweicloud_vpc_subnet" "stg_stg01" {
  region      = huaweicloud_vpc.stg.region
  name        = "STG01"
  cidr        = "10.2.1.0/24"
  gateway_ip  = "10.2.1.1"
  vpc_id      = huaweicloud_vpc.stg.id
  description = ""
  availability_zone = "sa-brazil-1b"
}

resource "huaweicloud_vpc_subnet" "prod_prod01" {
  region      = huaweicloud_vpc.prod.region
  name        = "PROD01"
  cidr        = "10.3.1.0/24"
  gateway_ip  = "10.3.1.1"
  vpc_id      = huaweicloud_vpc.prod.id
  description = ""
  availability_zone = "sa-brazil-1a"
}

resource "huaweicloud_vpc_subnet" "net_net01" {
  region      = huaweicloud_vpc.net.region
  name        = "NET01"
  cidr        = "10.4.1.0/24"
  gateway_ip  = "10.4.1.1"
  vpc_id      = huaweicloud_vpc.net.id
  description = ""
  availability_zone = "sa-brazil-1a"
}

