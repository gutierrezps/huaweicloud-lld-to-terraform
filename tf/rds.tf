data "huaweicloud_rds_flavors" "rds_mysql_app1" {
  region        = "sa-brazil-1"
  db_type       = "MySQL"
  db_version    = "8.0"
  instance_mode = "single"
  vcpus         = "2"
  memory        = "4"
  group_type    = "general"
}

resource "huaweicloud_rds_instance" "rds_mysql_app1" {
  name              = "rds-mysql-app1"
  flavor            = one(data.huaweicloud_rds_flavors.rds_mysql_app1.flavors).name
  vpc_id            = huaweicloud_vpc.prod.id
  subnet_id         = huaweicloud_vpc_subnet.prod_prod01.id
  security_group_id = huaweicloud_networking_secgroup.prd_sg001.id
  availability_zone = ["sa-brazil-1a"]
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  db {
    type     = "MySQL"
    version  = "8.0"
    password = "qwerty1234!#"
  }

  volume {
    type = "CLOUDSSD"
    size = 40
  }
}

data "huaweicloud_rds_flavors" "rds_pg_app1" {
  region        = "sa-brazil-1"
  db_type       = "PostgreSQL"
  db_version    = "14"
  instance_mode = "ha"
  vcpus         = "2"
  memory        = "8"
  group_type    = "dedicated"
}

resource "huaweicloud_rds_instance" "rds_pg_app1" {
  name              = "rds-pg-app1"
  flavor            = one(data.huaweicloud_rds_flavors.rds_pg_app1.flavors).name
  vpc_id            = huaweicloud_vpc.prod.id
  subnet_id         = huaweicloud_vpc_subnet.prod_prod01.id
  security_group_id = huaweicloud_networking_secgroup.prd_sg001.id
  availability_zone = ["sa-brazil-1a", "sa-brazil-1b"]
  ha_replication_mode = "async"
  enterprise_project_id = data.huaweicloud_enterprise_project.ep_prod.id

  db {
    type     = "PostgreSQL"
    version  = "14"
    password = "qwerty1234!#"
  }

  volume {
    type = "CLOUDSSD"
    size = 50
  }
}

