resource "huaweicloud_vpc_eip" "eip_dev01" {
  region  = "sa-brazil-1"
  name    = "eip-dev01"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  charging_mode = "postPaid"

  publicip {
    type = "5_bgp"
  }

  bandwidth {
    share_type  = "PER"
    name        = "bandwidth_eip-dev01"
    size        = 100
    charge_mode = "traffic"
  }
}

