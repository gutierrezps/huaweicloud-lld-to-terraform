# Changelog

## [Unreleased]

- **LLD**: Add Enterprise Project column to security group;
- **LLD**: Renamed "Enterprise Project Name" column in ECS tab to "Enterprise
  Project";
- Add Enterprise Project support to VPC, security group, ECS and EVS;
- Refactored servergroup dependencies, now creating servergroup first and then
  configuring their ID in ECS scheduler hints. This also removed the dependency
  of first NIC and EVS with the servergroup;
- Fix some inconsistencies in LLD examples;

## [0.2.0] - 2023-04-08

- New LLD template with more information;
- One security group per NIC;
- Refactored ECS reading into separate class;
- Add VPC, subnet and security group support;
- Add region to all resources.

## [0.1.0] - 2023-03-14

Initial version.
