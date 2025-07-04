# Changelog

## [Unreleased]

- Updated Terraform provider version to 1.76.1;
- Refactor Python automation to reduce code repetition (now using
  Resource2Terraform as base class).

## [0.4.0] - 2024-08-19

- **LLD**: Add EIP, NAT Gateway and NAT rules support;
- **metadata**: Add parameters for EIP, NAT and NATrules sheet names;
- Create separate files for provider configuration and variables (fix #1);
- Updated Terraform provider version to 1.67.1.

## [0.3.2] - 2023-09-21

- Add [LLD documentation](docs/LLD.md);
- Renamed `app.py` to `__main__.py`, command now is `python -m app`;
- Updated Terraform provider version to 1.55.0;
- Small cosmetic updates in the LLD spreadsheet (and added comment metadata
  with repository link and version).

## [0.3.1] - 2023-07-04

- Fix different security groups for different NICs not being set in
  `security_group_ids` of ECS resource;
- Fix ValueError exception not being handled.

## [0.3.0] - 2023-06-22

- **LLD**: Add Enterprise Project column to Security Group tag;
- **LLD**: Renamed "Enterprise Project Name" column in ECS tab to "Enterprise
  Project";
- **LLD**: Removed "Password or Keypair" column in ECS tab, because "OS
  Password" is mandatory in order to set a keypair;
- **metadata**: Added "ECS last wave" parameter;
- **LLD**: "Wave" column in ECS tab is now mandatory; if wave is negative or
  larger than "ECS last wave" parameter, the ECS will be ignored;
- **LLD**: Add "Dedicated Host" column to ECS tab;
- Add Enterprise Project support to VPC, security group, ECS and EVS;
- Refactored servergroup dependencies, now creating servergroup first and then
  configuring their ID in ECS scheduler hints. This also removed the dependency
  of first NIC and EVS with the servergroup;
- Fix tags in ECS and EVS;
- Add wave support;
- Add Dedicated Host support;
- Shared EVS now uses SCSI as device type (recommended by Console);
- Fix some inconsistencies in LLD examples;

## [0.2.0] - 2023-04-08

- New LLD template with more information;
- One security group per NIC;
- Refactored ECS reading into separate class;
- Add VPC, subnet and security group support;
- Add region to all resources.

## [0.1.0] - 2023-03-14

Initial version.
