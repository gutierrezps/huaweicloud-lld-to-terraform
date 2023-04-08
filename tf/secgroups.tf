resource "huaweicloud_networking_secgroup" "dev_sg001" {
  region  = "sa-brazil-1"
  name    = "dev-sg001"
  delete_default_rules = true
}

resource "huaweicloud_networking_secgroup_rule" "dev_sg001_rule01" {
  security_group_id = huaweicloud_networking_secgroup.dev_sg001.id
  direction         = "ingress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "119.138.50.11/32"
  priority          = 1
  description       = "DEV Access inbound"
}

resource "huaweicloud_networking_secgroup_rule" "dev_sg001_rule02" {
  security_group_id = huaweicloud_networking_secgroup.dev_sg001.id
  direction         = "egress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "0.0.0.0/0"
  priority          = 1
  description       = "DEV Access outbound"
}

resource "huaweicloud_networking_secgroup" "stg_sg001" {
  region  = "sa-brazil-1"
  name    = "stg-sg001"
  delete_default_rules = true
}

resource "huaweicloud_networking_secgroup_rule" "stg_sg001_rule01" {
  security_group_id = huaweicloud_networking_secgroup.stg_sg001.id
  direction         = "ingress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "119.138.50.12/32"
  priority          = 1
  description       = "STG Access inbound"
}

resource "huaweicloud_networking_secgroup_rule" "stg_sg001_rule02" {
  security_group_id = huaweicloud_networking_secgroup.stg_sg001.id
  direction         = "egress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "0.0.0.0/0"
  priority          = 1
  description       = "STG Access outbound"
}

resource "huaweicloud_networking_secgroup" "prd_sg001" {
  region  = "sa-brazil-1"
  name    = "prd-sg001"
  delete_default_rules = true
}

resource "huaweicloud_networking_secgroup_rule" "prd_sg001_rule01" {
  security_group_id = huaweicloud_networking_secgroup.prd_sg001.id
  direction         = "ingress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "119.138.50.13/32"
  priority          = 1
  description       = "PRD Access inbound"
}

resource "huaweicloud_networking_secgroup_rule" "prd_sg001_rule02" {
  security_group_id = huaweicloud_networking_secgroup.prd_sg001.id
  direction         = "egress"
  ethertype         = "IPv4"
  action            = "allow"
  remote_ip_prefix  = "0.0.0.0/0"
  priority          = 1
  description       = "PRD Access outbound"
}

