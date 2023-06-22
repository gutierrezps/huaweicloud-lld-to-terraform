resource "huaweicloud_compute_instance" "ecs_prod_01a" {
  name                = "ecs-prod-01a"
  image_id            = "68a783a4-25b2-4069-bc25-d927eeb7f97b"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.prd_sg001.id ]
  region              = "sa-brazil-1"
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "qwerty1234!#"
  system_disk_type    = "SSD"
  system_disk_size    = 50
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  network {
    uuid              = huaweicloud_vpc_subnet.prod_prod01.id
    fixed_ip_v4       = "10.3.1.10"
    source_dest_check = false
  }

  scheduler_hints {
    group         = huaweicloud_compute_servergroup.servergroup_group01.id
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_prod_01b" {
  name                = "ecs-prod-01b"
  image_id            = "68a783a4-25b2-4069-bc25-d927eeb7f97b"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.prd_sg001.id ]
  region              = "sa-brazil-1"
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "qwerty1234!#"
  system_disk_type    = "SSD"
  system_disk_size    = 50
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  network {
    uuid              = huaweicloud_vpc_subnet.prod_prod01.id
    fixed_ip_v4       = "10.3.1.11"
    source_dest_check = false
  }

  scheduler_hints {
    group         = huaweicloud_compute_servergroup.servergroup_group01.id
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_dev" {
  name                = "ecs-dev"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "t6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.dev_sg001.id ]
  region              = "sa-brazil-1"
  availability_zone   = "sa-brazil-1a"
  admin_pass          = "qwerty1234!#"
  key_pair            = "keypair-01"
  system_disk_type    = "SAS"
  system_disk_size    = 100
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  network {
    uuid              = huaweicloud_vpc_subnet.dev_dev01.id
    fixed_ip_v4       = "10.1.1.20"
    source_dest_check = true
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_stg" {
  name                = "ecs-stg"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "t6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.dev_sg001.id ]
  region              = "sa-brazil-1"
  availability_zone   = "sa-brazil-1a"
  admin_pass          = "qwerty1234!#"
  key_pair            = "keypair-01"
  system_disk_type    = "SAS"
  system_disk_size    = 100
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_stg.id

  network {
    uuid              = huaweicloud_vpc_subnet.stg_stg01.id
    fixed_ip_v4       = "10.2.1.21"
    source_dest_check = true
  }
}

resource "huaweicloud_compute_servergroup" "servergroup_group01" {
  region    = "sa-brazil-1"
  name      = "group01"
  policies  = ["anti-affinity"]
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_prod_01a_net_net01" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01a.id
  network_id  = huaweicloud_vpc_subnet.net_net01.id
  fixed_ip    = "10.4.1.10"
  security_group_ids  = [ huaweicloud_networking_secgroup.prd_sg001.id ]
  source_dest_check   = false
  depends_on  = [  ]
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_prod_01b_net_net01" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01b.id
  network_id  = huaweicloud_vpc_subnet.net_net01.id
  fixed_ip    = "10.4.1.11"
  security_group_ids  = [ huaweicloud_networking_secgroup.prd_sg001.id ]
  source_dest_check   = false
  depends_on  = [  ]
}

resource "huaweicloud_networking_vip" "vip_10_3_1_12" {
  region      = "sa-brazil-1"
  network_id  = huaweicloud_vpc_subnet.prod_prod01.id
  ip_address  = "10.3.1.12"
}

resource "huaweicloud_networking_vip_associate" "vip_10_3_1_12_associate" {
  region    = huaweicloud_networking_vip.vip_10_3_1_12.region
  vip_id    = huaweicloud_networking_vip.vip_10_3_1_12.id
  port_ids  = [
    huaweicloud_compute_instance.ecs_prod_01a.network[0].port,
    huaweicloud_compute_instance.ecs_prod_01b.network[0].port
  ]
}

resource "huaweicloud_networking_vip" "vip_10_4_1_12" {
  region      = "sa-brazil-1"
  network_id  = huaweicloud_vpc_subnet.net_net01.id
  ip_address  = "10.4.1.12"
}

resource "huaweicloud_networking_vip_associate" "vip_10_4_1_12_associate" {
  region    = huaweicloud_networking_vip.vip_10_4_1_12.region
  vip_id    = huaweicloud_networking_vip.vip_10_4_1_12.id
  port_ids  = [
    split("/", huaweicloud_compute_interface_attach.nic_ecs_prod_01a_net_net01.id)[1],
    split("/", huaweicloud_compute_interface_attach.nic_ecs_prod_01b_net_net01.id)[1]
  ]
}

resource "huaweicloud_evs_volume" "evs_ecs_prod_01_data_1_shared" {
  name              = "ecs_prod_01_data_1_shared"
  region            = "sa-brazil-1"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SSD"
  size              = 1024
  multiattach       = true
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_prod_01a_data_2" {
  name              = "ecs_prod_01a_data_2"
  region            = "sa-brazil-1"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_prod_01b_data_2" {
  name              = "ecs_prod_01b_data_2"
  region            = "sa-brazil-1"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_dev_data_1" {
  name              = "ecs_dev_data_1"
  region            = "sa-brazil-1"
  availability_zone = "sa-brazil-1a"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_dev_data_2" {
  name              = "ecs_dev_data_2"
  region            = "sa-brazil-1"
  availability_zone = "sa-brazil-1a"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_dev.id

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_prod_01_data_1_shareda_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01a.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_prod_01_data_1_shared.id
  device = "/dev/vdb"
  depends_on = [  ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_prod_01a_data_2_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01a.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_prod_01a_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_prod_01_data_1_shareda_attachment ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_prod_01_data_1_sharedb_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01b.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_prod_01_data_1_shared.id
  device = "/dev/vdb"
  depends_on = [  ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_prod_01b_data_2_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_prod_01b.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_prod_01b_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_prod_01_data_1_sharedb_attachment ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_dev_data_1_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_dev.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_dev_data_1.id
  device = "/dev/vdb"
  depends_on = [  ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_dev_data_2_attachment" {
  region      = "sa-brazil-1"
  instance_id = huaweicloud_compute_instance.ecs_dev.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_dev_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_dev_data_1_attachment ]
  timeouts {
    create = "20m"
  }
}

