resource "huaweicloud_nat_gateway" "nat_gw" {
  region      = "sa-brazil-1"
  name        = "nat-gw"
  description = "DEV NAT Gateway"
  spec        = "1"
  vpc_id      = huaweicloud_vpc.dev.id
  subnet_id   = huaweicloud_vpc_subnet.dev_dev01.id
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id
}

data "huaweicloud_networking_port" "nat_gw_dnat_rule01_port" {
  network_id = huaweicloud_vpc_subnet.dev_dev01.id
  fixed_ip   = "10.1.1.20"
}

resource "huaweicloud_nat_dnat_rule" "nat_gw_dnat_rule01" {
  region                = huaweicloud_nat_gateway.nat_gw.region
  nat_gateway_id        = huaweicloud_nat_gateway.nat_gw.id
  floating_ip_id        = huaweicloud_vpc_eip.eip_dev01_inbound.id
  description           = ""
  port_id               = data.huaweicloud_networking_port.nat_gw_dnat_rule01_port.port_id
  protocol              = "tcp"
  internal_service_port = 80
  external_service_port = 80
}

resource "huaweicloud_nat_snat_rule" "nat_gw_snat_rule02" {
  region          = huaweicloud_nat_gateway.nat_gw.region
  nat_gateway_id  = huaweicloud_nat_gateway.nat_gw.id
  floating_ip_id  = huaweicloud_vpc_eip.eip_dev01_outbound.id
  description     = ""
  subnet_id       = huaweicloud_vpc_subnet.dev_dev01.id
}

