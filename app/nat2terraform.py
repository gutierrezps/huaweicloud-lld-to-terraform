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

    def _parse(self, nat_data: dict):
        nat_data['subnet'] = nat_data['vpc'] + '_' + nat_data['subnet']
        return super()._parse(nat_data)
