resource "huaweicloud_compute_instance" "ecs_1_01a" {
  name                = "ecs-1-01a"
  image_id            = "68a783a4-25b2-4069-bc25-d927eeb7f97b"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SAS"
  system_disk_size    = 50

  network {
    uuid              = huaweicloud_vpc_subnet.prod_subnet_prod_1.id
    fixed_ip_v4       = "10.1.1.10"
    source_dest_check = false
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_1_01b" {
  name                = "ecs-1-01b"
  image_id            = "68a783a4-25b2-4069-bc25-d927eeb7f97b"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SAS"
  system_disk_size    = 50

  network {
    uuid              = huaweicloud_vpc_subnet.prod_subnet_prod_1.id
    fixed_ip_v4       = "10.1.1.11"
    source_dest_check = false
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_1_02" {
  name                = "ecs-1-02"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "t6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1a"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SSD"
  system_disk_size    = 100

  network {
    uuid              = huaweicloud_vpc_subnet.prod_subnet_prod_1.id
    fixed_ip_v4       = "10.1.1.20"
    source_dest_check = true
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_1_03" {
  name                = "ecs-1-03"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "t6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1a"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SSD"
  system_disk_size    = 100

  network {
    uuid              = huaweicloud_vpc_subnet.prod_subnet_prod_1.id
    fixed_ip_v4       = "10.1.1.21"
    source_dest_check = true
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_servergroup" "servergroup_group01" {
  name     = "group01"
  policies = ["anti-affinity"]
  members  = [
    huaweicloud_compute_instance.ecs_1_01a.id,
    huaweicloud_compute_instance.ecs_1_01b.id
  ]
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_1_01a_sync_subnet_sync_1" {
  instance_id = huaweicloud_compute_instance.ecs_1_01a.id
  network_id  = huaweicloud_vpc_subnet.sync_subnet_sync_1.id
  fixed_ip    = "10.2.1.10"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  source_dest_check   = false
  depends_on  = [ huaweicloud_compute_servergroup.servergroup_group01 ]
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_1_01b_sync_subnet_sync_1" {
  instance_id = huaweicloud_compute_instance.ecs_1_01b.id
  network_id  = huaweicloud_vpc_subnet.sync_subnet_sync_1.id
  fixed_ip    = "10.2.1.11"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  source_dest_check   = false
  depends_on  = [ huaweicloud_compute_servergroup.servergroup_group01 ]
}

resource "huaweicloud_networking_vip" "vip_10_1_1_12" {
  network_id = huaweicloud_vpc_subnet.prod_subnet_prod_1.id
  ip_address = "10.1.1.12"
}

resource "huaweicloud_networking_vip_associate" "vip_10_1_1_12_associate" {
  vip_id   = huaweicloud_networking_vip.vip_10_1_1_12.id
  port_ids = [
    huaweicloud_compute_instance.ecs_1_01a.network[0].port,
    huaweicloud_compute_instance.ecs_1_01b.network[0].port
  ]
}

resource "huaweicloud_networking_vip" "vip_10_2_1_12" {
  network_id = huaweicloud_vpc_subnet.sync_subnet_sync_1.id
  ip_address = "10.2.1.12"
}

resource "huaweicloud_networking_vip_associate" "vip_10_2_1_12_associate" {
  vip_id   = huaweicloud_networking_vip.vip_10_2_1_12.id
  port_ids = [
    split("/", huaweicloud_compute_interface_attach.nic_ecs_1_01a_sync_subnet_sync_1.id)[1],
    split("/", huaweicloud_compute_interface_attach.nic_ecs_1_01b_sync_subnet_sync_1.id)[1]
  ]
}

resource "huaweicloud_evs_volume" "evs_ecs_1_01_data_1_shared" {
  name              = "ecs_1_01_data_1_shared"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 1024
  multiattach       = true

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_1_01a_data_2" {
  name              = "ecs_1_01a_data_2"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_1_01b_data_2" {
  name              = "ecs_1_01b_data_2"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_1_02_data_1" {
  name              = "ecs_1_02_data_1"
  availability_zone = "sa-brazil-1a"
  volume_type       = "SSD"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_1_02_data_2" {
  name              = "ecs_1_02_data_2"
  availability_zone = "sa-brazil-1a"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_01_data_1_shareda_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_01a.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_01_data_1_shared.id
  device = "/dev/vdb"
  depends_on = [ huaweicloud_compute_servergroup.servergroup_group01 ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_01a_data_2_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_01a.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_01a_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_1_01_data_1_shareda_attachment ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_01_data_1_sharedb_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_01b.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_01_data_1_shared.id
  device = "/dev/vdb"
  depends_on = [ huaweicloud_compute_servergroup.servergroup_group01 ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_01b_data_2_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_01b.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_01b_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_1_01_data_1_sharedb_attachment ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_02_data_1_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_02.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_02_data_1.id
  device = "/dev/vdb"
  depends_on = [  ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_1_02_data_2_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_1_02.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_1_02_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_1_02_data_1_attachment ]
  timeouts {
    create = "20m"
  }
}

