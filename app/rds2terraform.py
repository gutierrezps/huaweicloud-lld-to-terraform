from .resource2terraform import Resource2Terraform


class Rds2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='rds', key_attr='rds')
        self._attr_clean = {
            'rds': 'rds_name',
            'secgroup': 'security_group',
            'vpc_name': 'vpc_name',
            'subnet_name': 'subnet_name',
            'project': 'enterprise_project'
        }

    def _parse(self, resource_data: dict):
        subnet = f"{resource_data['vpc_name']}_{resource_data['subnet_name']}"
        resource_data['subnet'] = subnet

        availability_zones = [
           resource_data['primary_az']
        ]
        if resource_data['db_instance_mode'] == 'ha':
            availability_zones.append(resource_data['standby_az'])
            resource_data['ha_replication'] = "async"

        resource_data['availability_zones'] = '", "'.join(availability_zones)

        return super()._parse(resource_data)
