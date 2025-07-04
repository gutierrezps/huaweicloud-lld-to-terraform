# Low-Level Design (LLD)

This document contains the description of each tab in the `LLD.xlsx` spreadsheet
and the associated arguments reference.

- [Low-Level Design (LLD)](#low-level-design-lld)
  - [General orientations](#general-orientations)
  - [Enterprise Project](#enterprise-project)
    - [EPS Argument Reference](#eps-argument-reference)
  - [Virtual Private Cloud (VPC)](#virtual-private-cloud-vpc)
    - [VPC Argument Reference](#vpc-argument-reference)
  - [Subnet](#subnet)
    - [Subnet Argument Reference](#subnet-argument-reference)
  - [Security Group (secgroup)](#security-group-secgroup)
    - [Secgroup Argument Reference](#secgroup-argument-reference)
  - [Elastic IP (EIP)](#elastic-ip-eip)
    - [EIP Argument Reference](#eip-argument-reference)
  - [NAT Gateway](#nat-gateway)
    - [Public NAT Gateway instance Argument Reference](#public-nat-gateway-instance-argument-reference)
    - [NAT Rules Argument Reference](#nat-rules-argument-reference)
  - [Elastic Cloud Server (ECS)](#elastic-cloud-server-ecs)
    - [ECS Argument Reference](#ecs-argument-reference)
  - [Relational Database Service (RDS)](#relational-database-service-rds)
    - [RDS Argument Reference](#rds-argument-reference)

## General orientations

The first row is the header row, and its values are read as argument names.
Each subsequent row is considered a resource instance, and each column is read
as the respective argument value for that resource instance.

Each argument can have the following attributes (specified between
parenthesis):

- required: mandatory argument, must be filled;
- optional: optional argument, can be left blank/empty;
- force new: if argument value is changed, a new instance is created because
  the Terraform provider or the HUAWEI CLOUD API does not support value updates
  for said argument. Review the execution plan carefully when updating such
  arguments;
- not used: argument is not used by the LLD to Terraform tool, so it can be
  filled with any value or can be removed entirely;
- resource name: argument value is used to generate resource names and
  references in Terraform code. If the value is changed, manual work is needed
  in the Terraform side in order to prevent data loss (particularly for
  enterprise project name, VPC name, subnet name and ECS hostname), either by
  using the [`terraform state mv`][tf-state-mv] command or the
  [`moved`][tf-moved] configuration block. Review the execution plan carefully
  when updating such arguments.

## Enterprise Project

[Enterprise Project Management Service (EPS)][eps] provides a cloud governance
platform that matches the organizational structure and service management model
of your enterprise. It provides enterprise project, resource, personnel,
accounting, and application management.

Each row of the spreadsheet corresponds to one enterprise project. Since
Enterprise projects cannot be deleted, they need to be created manually in
the Console and then listed in the spreadsheet.

Enterprise project configuration is optional.

### EPS Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Name** - (required, resource name) Name of an existing enterprise project.
  The tool will not create the enterprise project if it doesn't exist.
- **Project Type** - (optional, not used) Type of the enterprise project.
- **Description** - (optional, not used) Description of the enterprise project.

## Virtual Private Cloud (VPC)

The [Virtual Private Cloud (VPC)][vpc] service enables you to provision
logically isolated virtual private networks for cloud resources, such cloud
servers, containers, and databases.

Each row of the spreadsheet corresponds to one VPC.

### VPC Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the VPC. See [Regions and Endpoints][endpoints] to get the desired
  region code. Changing this creates a new VPC.
- **VPC Name** - (required, resource name) Name of the VPC, must be unique for
  the account. The value is a string of no more than 64 characters and can
  contain digits, letters, underscores (_), and hyphens (-).
- **IPv4 CIDR Block** - (required) Range of available subnets in the VPC. The
  value ranges from 10.0.0.0/8 to 10.255.255.0/24, 172.16.0.0/12 to
  172.31.255.0/24, or 192.168.0.0/16 to 192.168.255.0/24.
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where VPC will be created. If this argument is set, the enterprise project
  must be specified in the associated spreadsheet tab. Changing this creates
  a new VPC.
- **Description** - (optional) Supplementary information about the VPC. The
  value can be a string of no more than 255 characters and cannot contain
  angle brackets (< or >).

## Subnet

A subnet is a unique CIDR block with a range of IP addresses in a VPC. All
resources in a VPC must be deployed on subnets.

Each row of the spreadsheet corresponds to one subnet.

### Subnet Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **VPC Name** - (required, force new) Name of the VPC specified in the
  associated spreadsheet tab. Changing this creates a new subnet.
- **AZ** - (required, force new) Availability Zone code (e.g. `sa-brazil-1a`)
  in which to create the subnet. See [Regions and Endpoints][endpoints] to get
  the desired availability zone code. Changing this creates a new subnet.
- **Subnet Name** - (required, resource name) Name of the subnet. The value is
  a string of no more than 64 characters and can contain digits, letters,
  underscores (_) and hyphens (-).
- **IPv4 CIDR Block** - (required, force new) Network segment on which the
  subnet resides. The value must be in CIDR format and within the CIDR block of
  the VPC. The subnet mask cannot be greater than 28. Changing this creates a
  new subnet.
- **Gateway** - (required, force new) IP address of the gateway of the subnet.
  The value must be a valid IP address in the subnet segment. Changing this
  creates a new subnet.
- **Description** - (optional) Supplementary information about the subnet. The
  value can be a string of no more than 255 characters and cannot contain
  angle brackets (< or >).

## Security Group (secgroup)

A [security group][secgroup] is a collection of access control rules for cloud
resources, such as cloud servers, containers, and databases, that have the same
security protection requirements and that are mutually trusted.

Each row of the spreadsheet corresponds to one security group rule. Security
groups will also be created using the unique values of the security group name
column.

If it is not desired to manage security group rules using Terraform (because
they need to be updated constantly or in a timely manner, for example), add
only a single rule for each security group (egress allowed to 0.0.0.0/0 for
example) so that the security group can be used in the ECS spreadsheet tab.

### Secgroup Argument Reference

Although almost all arguments have the "force new" attribute, value changes do
not incur data loss, but will appear as destroy and create actions in the
execution plan. The order of the rules of the same security group is also
used to build the resource names in the Terraform code. Again, review the
execution plan carefully when updating such values or when inserting new
security group rules.

- **SN** - (optional, not used) Serial number, only for reference.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the VPC. See [Regions and Endpoints][endpoints] to get the desired
  region code.
- **Security Group Name** - (required, resource name) Name of the security
  group which will contain the rule. The value is a string of no more than 64
  characters and can contain digits, letters, underscores (_), and hyphens (-).
- **Direction** - (required, force new) Traffic direction of the rule, valid
  values are **ingress** and **egress**.
- **Priority** - (optional, force new) Priority number. Valid value is an
  integer from 1 to 100. Default value is 1.
- **Action** - (required, force new) Effective rule policy. The valid values
  are **allow** and **deny**.
- **Protocol** - (optional, force new) Layer 4 protocol type, valid values are
  **all**, **tcp**, **udp**, **icmp** or **icmpv6**. If omitted, the protocol
  means that all protocols are supported.
- **Ports** - (optional, force new) Allowed port value range, which supports
  **all**, single port (e.g. **80**), continuous port (e.g. **1-30**) and
  discontinous port (**22, 3389, 80**). The valid port values is range form 1
  to 65535.
- **Type** - (required, force new) Layer 3 protocol type, valid values are
  **IPv4** and **IPv6**.
- **Destination/Source** - (required, force new) Remote IP CIDR, the value
  needs to be a valid CIDR (e.g. **192.168.0.0/16** for a IP range,
  **192.168.0.10/32** for a single address or **0.0.0.0/0** for any address).
- **Description** - (optional) Supplementary information about the networking
  security group rule. This parameter can contain a maximum of 255 characters
  and cannot contain angle brackets (< or >).
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where the security group will be created. If this argument is set, the
  enterprise project must be specified in the associated spreadsheet tab.

## Elastic IP (EIP)

An [Elastic IP (EIP)][eip] is a public IP address that can be accessed directly
over the Internet. An EIP consists of a public IP address and some amount of
public network egress bandwidth. EIPs can be bound to or unbound from ECSs,
BMSs, virtual IP addresses, NAT gateways, and load balancers.

Each row of the spreadsheet corresponds to one EIP address.

### EIP Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the EIP. See [Regions and Endpoints][endpoints] to get the desired
  region code.
- **EIP Name** - (required, resource name) Name of the EIP, which is also used
  to compose the bandwidth name. The value is a string of no more than 64
  characters and can contain digits, letters, underscores (_), and hyphens (-).
- **Charge Mode** - (required) Specifies whether the bandwidth is billed by
  traffic or by bandwidth size. The value can be `traffic` or `bandwidth`.
- **Size Mbit** - (required) Bandwidth size in Mbit/s. Valid value is integer
  from 1 to 300.
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where the Elastic IP will be created. If this argument is set, the
  enterprise project must be specified in the associated spreadsheet tab.

## NAT Gateway

[NAT Gateway][nat] is a network address translation (NAT) service. A public NAT
gateway enables cloud and on-premises servers in a private subnet to share an
EIP to access the Internet (through a SNAT Rule) or provide services accessible
from the Internet (through a DNAT Rule).

Each row of the spreadsheet `NAT` corresponds to one public NAT Gateway instance.

Each row of the spreadsheet `NATrules` corresponds to one SNAT/DNAT rule in the
specified NAT Gateway.

### Public NAT Gateway instance Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the public NAT Gateway. See [Regions and Endpoints][endpoints] to
  get the desired region code. Changing this creates a new NAT Gateway.
- **NAT Name** - (required, resource name) Name of the NAT Gateway, which is
  also used to compose NAT rules names. The value is a string of no more than 64
  characters and can contain digits, letters, underscores (_), and hyphens (-).
- **VPC Name** - (required, force new) Name of the VPC specified in the
  associated spreadsheet tab. Changing this creates a new NAT Gateway.
- **Subnet Name** - (required, force new) Name of the subnet specified in the
  associated spreadsheet tab. Changing this creates a new NAT Gateway.
- **Scale** - (required) Specification of the NAT gateway. Valid values is
  integer from `1` to `4`, where `1` corresponds to Small type, and `4`
  correspons to Extra-large type.
- **Private IP** - (optional, force new) Private IP address of NAT gateway,
  which must be within the subnet range. Changing this creates a new NAT Gateway.
- **Description** - (optional) Supplementary information about the NAT Gateway.
  This parameter can contain a maximum of 255 characters and cannot contain
  angle brackets (< or >).
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where the NAT gateway will be created. If this argument is set, the
  enterprise project must be specified in the associated spreadsheet tab.

### NAT Rules Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **NAT Name** - (required, resource name) Name of the NAT Gateway specified in
  the associated spreadsheet tab.
- **Rule Type** - (required, force new) Direction of the rule, valid
  values are **DNAT** (inbound/ingress) and **SNAT** (outbound/egress).
- **EIP Name** - (required, force new) Name of the EIP specified in the
  associated spreadsheet tab. Changing this creates a new NAT rule.
- **Description** - (optional) Supplementary information about the NAT rule.
  This parameter can contain a maximum of 255 characters and cannot contain
  angle brackets (< or >).

For DNAT rules, the following arguments are supported:

> Before creating a DNAT rule, make sure the resource is already created in the
> target subnet, otherwise the following error message will be displayed when
> applying changes: `Error: no networking port found`. If this happens,
> run the Terraform command again.

- **DNAT External Port** - (required) Specifies port used in EIP to provide
  services for external systems.
- **DNAT Subnet Name** - (required) Name of the subnet specified in the
  associated spreadsheet tab. Subnet where the resource is located.
- **DNAT Internal IP** - (required) Private IP address of the resource, already
  existing in the subnet.
- **DNAT Internal Port** - (required) Specifies port used by resource (e.g. ECS)
  to provide services for external systems.

For SNAT rules, the following arguments are supported:

- **SNAT CIDR/subnet** - (required, force new) Specify the CIDR block (e.g.
  `10.0.0.0/8`) or the subnet name (specified in the associated spreadsheet tab)
  which will be connected by SNAT rule. Changing this will create a new SNAT
  rule.

## Elastic Cloud Server (ECS)

An [Elastic Cloud Server (ECS)][ecs] is a basic computing unit that consists of
vCPUs, memory, OS and Elastic Volume Service (EVS) disks.

Each row of the spreadsheet corresponds to one ECS.

### ECS Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where the ECS will be created. If this argument is set, the enterprise
  project must be specified in the associated spreadsheet tab. Changing this
  creates a new ECS.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the VPC. See [Regions and Endpoints][endpoints] to get the desired
  region code. Changing this creates a new ECS.
- **AZ** - (required, force new) Availability Zone code (e.g. `sa-brazil-1a`)
  in which to create the subnet. See [Regions and Endpoints][endpoints] to get
  the desired availability zone code. Changing this creates a new ECS.
- **Hostname** - (required, resource name) Unique name for the ECS. The name
  consists of 1 to 64 characters, including letters, digits, underscores (_),
  hyphens (-), and periods (.).
- **Wave** - (required) Integer value, controls if the Terraform code for the
  ECS and associated EVSs will be generated or not. If the wave number is zero,
  negative or greater than the "Resource last wave" value set in the
  **metadata.xlsx** spreadsheet, the Terraform code will not be generated.
- **ECS Group** - (optional, resource name, force new) Name of the server
  group where the instance will be placed. A [server group][ecs-group] with
  this name will be created. This parameter can contain a maximum of 255
  characters, which may consist of letters, digits, underscores (_), and
  hyphens (-). This argument is required if the ECS has one or more shared data
  disks. Changing this creates a new ECS.
- **Dedicated Host** - (optional, force new) Specifies whether the ECS is to be
  created on a Dedicated Host (DeH). Valid values are **yes** or **no**. If
  left blank or set to **no**, ECS will be created in the shared pool (default
  ECS behavior). Changing this creates a new ECS.
- **Flavor** - (required) Flavor Name of the ECS to be created (e.g.
  **s6.small.1**). Check the [ECS purchase page][ecs-buy] with the desired
  Region and AZ selected to obtain the flavors available.
- **Image name** - (optional, not used) Name of the desired IMS image for the
  instance, only for reference.
- **Image ID** - (required, force new) IMS Image ID of the desired image for
  the instance. Check the [IMS image list][ims-list] in the desired Region to
  obtain the ID of the desired image, which can be Public, Private or Shared.
  Changing this creates a new ECS.
- **OS Password** - (required) Initial login password of the administrator
  account for logging in to an ECS using password authentication. The Linux
  administrator is root, and the Windows administrator is Administrator. This
  configuration will only take effect for public images or for images with
  Cloud-Init installed. Consists of 8 to 26 characters. The password must
  contain at least three of the following character types: uppercase letters,
  lowercase letters, digits, and special characters (`!@$%^-_=+[{}]:,./?~#*`).
  The password cannot contain the username or the username in reverse.
- **Keypair Name** - (optional) Name of the SSH key used for logging in to the
  ECS. The key pair must be created previously in the [KPS service][kps].
  Even if this authentication method is selected, the OS password must be
  specified.

Each ECS can have up to 8 Network Interface Cards (NICs). Replace `#` in the
argument name by the NIC index, between 1 and 8. NIC1 information is required,
while NIC2 onward is optional. Only NIC1 and NIC2 columns are present in the
default `LLD.xlsx` file, more columns can be added for other NICs, always
following the same pattern. Each ECS flavor has a different number of maximum
NICs that are supported, [check the documentation][ecs-flavors].

- **NIC# VPC** - (required, force new) Name of the VPC specified in the
  associated spreadsheet tab. Changing this for NIC1 creates a new ECS.
  Changing this for NIC2 onward creates a new NIC.
- **NIC# Subnet** - (required, force new, resource name) Name of the subnet
  specified in the associated spreadsheet tab. Changing this for NIC1
  creates a new ECS. Changing this for NIC2 onward creates a new NIC.
- **NIC# Security Group** - (required) Name of the security group specified in
  the associated spreadsheet tab.
- **NIC# Fixed IP** - (required, force new) Fixed IPv4 address to be used on
  this subnet. Changing this for NIC1 creates a new ECS. Changing this for NIC2
  onward creates a new NIC.
- **NIC# Virtual IP** - (optional, force new, resource name)
  [Virtual IP address][vip] to be assigned to this NIC. Multiple NICs can share
  the same Virtual IP. Changing this creates a new Virtual IP instance.

System disk specifications:

- **System Disk Type** - (required, force new) Disk type code. Valid values
  are **SAS** (High I/O), **SSD** (Ultra-high I/O), **GPSSD** (General purpose
  SSD) and **ESSD** (Extreme SSD). Changing this creates a new EVS.
- **System Disk Size** - (required) Disk size in GB. Valid value is integer
  from 40 to 1024. Minimum value depends on the image size being used.
  Shrinking the disk is not supported.

Each ECS can have up to 23 EVS data disks. Replace `#` in the argument name by
the EVS index, between 1 and 23. Only data disk 1 and 2 columns are present in
the default `LLD.xlsx` file, more columns can be added for other data disks,
always following the same pattern. Data disks are optional.

- **Data Disk # Type** - (required, force new) Disk type code. Valid values
  are **SAS** (High I/O), **SSD** (Ultra-high I/O), **GPSSD** (General purpose
  SSD) and **ESSD** (Extreme SSD). Changing this creates a new EVS.
- **Data Disk # Size** - (required) Disk size in GB. Valid value is integer
  from 10 to 32768. Shrinking the disk is not supported.
- **Data Disk # Shared** - (required, force new) If the disk is shared or not.
  Valid values are **yes** and **no**. If set to **yes**, the disk will be
  considered to be shared between the ECSs in the same server group (argument
  **ECS Group**).

## Relational Database Service (RDS)

The [Relational Database Service (RDS)][rds] is a cloud-based web service that
is reliable, scalable, easy to manage, and ready for immediate use.

Each row of the spreadsheet corresponds to one RDS instance.

### RDS Argument Reference

- **SN** - (optional, not used) Serial number, only for reference.
- **Region** - (required, force new) Region code (e.g. `sa-brazil-1`) in which
  to create the RDS. See [Regions and Endpoints][endpoints] to get the desired
  region code. Changing this creates a new RDS.
- **RDS Name** - (required, resource name) Name of the RDS, must be unique for
  the account. The value is a string of no more than 64 characters and can
  contain digits, letters, underscores (_), and hyphens (-).
- **Wave** - (required) Integer value, controls if the Terraform code for the
  RDS will be generated or not. If the wave number is zero, negative or greater
  than the "Resource last wave" value set in the **metadata.xlsx** spreadsheet,
  the Terraform code will not be generated.
- **vCPUs** - (required) Integer value, specifies the number of vCPUs in the
  RDS flavor.
- **Memory GB** - (required) Integer value, specifies the memory size (GB) in
  the RDS flavor.
- **Instance Class** - (required) Specifies the performance specification, the
  valid values are `general` and `dedicated`.
- **DB Engine** - (required) Specifies the DB engine. The value can be `MySQL`
  and `PostgreSQL`.
- **DB Engine Version** - (required) Specifies the database version.
- **DB Instance Mode** - (required) Specifies the mode of instance. The value
  can be `single` (single instance) or `ha` (primary/standby instance).
- **Password** - (required) Specifies the database password. The value should
  contain 8 to 32 characters, including uppercase and lowercase letters, digits,
  and the following special characters: `~!@#%^*-_=+?` You are advised to enter
  a strong password to improve security, preventing security risks such as
  brute force cracking.
- **Primary AZ** - (required) Availability Zone code (e.g. `sa-brazil-1a`)
  in which to create the primary instance (or single instance). See
  [Regions and Endpoints][endpoints] to get the desired availability zone code.
- **Standby AZ** - (optional) Availability Zone code (e.g. `sa-brazil-1a`)
  in which to create the standby instance. See [Regions and Endpoints][endpoints]
  to get the desired availability zone code. This parameter is mandatory when
  **DB Instance Mode** is set to `ha`.
- **Storage Size** - (required) Integer value, specifies the volume size. Its
  value range is from 40 GB to 4000 GB. The value must be a multiple of 10.
- **VPC Name** - (required, force new) Name of the VPC specified in the
  associated spreadsheet tab. Changing this creates a new RDS instance.
- **Subnet Name** - (required, force new) Name of the subnet specified in the
  associated spreadsheet tab. Changing this creates a new RDS instance.
- **Security Group** - (required) Name of the security group specified in the
  associated spreadsheet tab.
- **Enterprise Project** - (optional, force new) Name of enterprise project
  where RDS will be created. If this argument is set, the enterprise project
  must be specified in the associated spreadsheet tab. Changing this creates
  a new RDS.
- **Description** - (optional) Supplementary information about the RDS. The
  value can be a string of no more than 255 characters and cannot contain
  angle brackets (< or >).

[tf-state-mv]: <https://developer.hashicorp.com/terraform/cli/commands/state/mv>
[tf-moved]: <https://developer.hashicorp.com/terraform/tutorials/configuration-language/move-config>
[eps]: <https://support.huaweicloud.com/intl/en-us/usermanual-em/em_eps_01_0000.html>
[vpc]: <https://support.huaweicloud.com/intl/en-us/productdesc-vpc/en-us_topic_0013748729.html>
[endpoints]: <https://developer.huaweicloud.com/intl/en-us/endpoint>
[secgroup]: <https://support.huaweicloud.com/intl/en-us/productdesc-vpc/vpc_Concepts_0005.html>
[ecs]: <https://support.huaweicloud.com/intl/en-us/productdesc-ecs/en-us_topic_0013771112.html>
[ecs-group]: <https://support.huaweicloud.com/intl/en-us/usermanual-ecs/ecs_03_0150.html>
[ecs-buy]: <https://console-intl.huaweicloud.com/ecm/#/ecs/createVm>
[ims-list]: <https://console-intl.huaweicloud.com/ecm/#/ims/manager/imageList/publicImage>
[kps]: <https://support.huaweicloud.com/intl/en-us/usermanual-dew/dew_01_0034.html>
[ecs-flavors]: <https://support.huaweicloud.com/intl/en-us/productdesc-ecs/ecs_01_0014.html>
[vip]: <https://support.huaweicloud.com/intl/en-us/productdesc-vpc/vpc_Concepts_0012.html>
[eip]: <https://support.huaweicloud.com/intl/en-us/productdesc-eip/overview_0001.html>
[nat]: <https://support.huaweicloud.com/intl/en-us/productdesc-natgateway/en-us_topic_0086739762.html>
[rds]: <https://support.huaweicloud.com/intl/en-us/productdesc-rds/en-us_topic_dashboard.html>
