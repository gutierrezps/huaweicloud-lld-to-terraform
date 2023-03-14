resource "huaweicloud_compute_instance" "ecs_2_01" {
  name                = "ecs-2-01"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SSD"
  system_disk_size    = 100

  network {
    uuid              = huaweicloud_vpc_subnet.subnet_prod_2.id
    fixed_ip_v4       = "10.1.2.20"
    source_dest_check = true
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_instance" "ecs_2_02" {
  name                = "ecs-2-02"
  image_id            = "3075b5b0-bc15-4998-97b6-7c3d5eb5d911"
  flavor_id           = "s6.small.1"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  availability_zone   = "sa-brazil-1b"
  admin_pass          = "Huawei@1234"
  system_disk_type    = "SSD"
  system_disk_size    = 100

  network {
    uuid              = huaweicloud_vpc_subnet.subnet_prod_2.id
    fixed_ip_v4       = "10.1.2.21"
    source_dest_check = true
  }

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_2_01_subnet_sync_2" {
  instance_id = huaweicloud_compute_instance.ecs_2_01.id
  network_id  = huaweicloud_vpc_subnet.subnet_sync_2.id
  fixed_ip    = "10.2.2.20"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  source_dest_check   = true
  depends_on  = [  ]
}

resource "huaweicloud_compute_interface_attach" "nic_ecs_2_02_subnet_sync_2" {
  instance_id = huaweicloud_compute_instance.ecs_2_02.id
  network_id  = huaweicloud_vpc_subnet.subnet_sync_2.id
  fixed_ip    = "10.2.2.21"
  security_group_ids  = [ huaweicloud_networking_secgroup.sg_prod.id ]
  source_dest_check   = true
  depends_on  = [  ]
}

resource "huaweicloud_evs_volume" "evs_ecs_2_01_data_1" {
  name              = "ecs_2_01_data_1"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SSD"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_evs_volume" "evs_ecs_2_01_data_2" {
  name              = "ecs_2_01_data_2"
  availability_zone = "sa-brazil-1b"
  volume_type       = "SAS"
  size              = 512
  multiattach       = false

  tags = {
    deployed_by   = "terraform"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_2_01_data_1_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_2_01.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_2_01_data_1.id
  device = "/dev/vdb"
  depends_on = [  ]
  timeouts {
    create = "20m"
  }
}

resource "huaweicloud_compute_volume_attach" "evs_ecs_2_01_data_2_attachment" {
  instance_id = huaweicloud_compute_instance.ecs_2_01.id
  volume_id   = huaweicloud_evs_volume.evs_ecs_2_01_data_2.id
  device = "/dev/vdc"
  depends_on = [ huaweicloud_compute_volume_attach.evs_ecs_2_01_data_1_attachment ]
  timeouts {
    create = "20m"
  }
}

