resource "huaweicloud_vpc_eip" "eip_dev01_inbound" {
  region  = "sa-brazil-1"
  name    = "eip-dev01-inbound"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  charging_mode = "postPaid"

  publicip {
    type = "5_bgp"
  }

  bandwidth {
    share_type  = "PER"
    name        = "bandwidth-eip-dev01-inbound"
    size        = 100
    charge_mode = "traffic"
  }
}

resource "huaweicloud_vpc_eip" "eip_dev01_outbound" {
  region  = "sa-brazil-1"
  name    = "eip-dev01-outbound"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  charging_mode = "postPaid"

  publicip {
    type = "5_bgp"
  }

  bandwidth {
    share_type  = "PER"
    name        = "bandwidth-eip-dev01-outbound"
    size        = 100
    charge_mode = "traffic"
  }
}

