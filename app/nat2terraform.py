from .resource2terraform import Resource2Terraform


class Nat2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='nat', key_attr='nat')
        self._attr_clean = {
            'nat': 'nat_name',
            'subnet': 'subnet_name',
            'vpc': 'vpc_name',
            'project': 'enterprise_project'
        }

    def _parse(self, resource_data: dict):
        subnet = resource_data['vpc'] + '_' + resource_data['subnet']
        resource_data['subnet'] = subnet
        return super()._parse(resource_data)
