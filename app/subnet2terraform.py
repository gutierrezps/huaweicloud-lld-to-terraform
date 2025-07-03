from .resource2terraform import Resource2Terraform


class Subnet2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='subnet', key_attr='subnet')
        self._attr_clean = {
            'subnet': 'subnet_name',
            'vpc': 'vpc_name'
        }

    def _parse(self, resource_data: dict):
        subnet = f"{resource_data['vpc']}_{resource_data['subnet']}"
        resource_data['subnet'] = subnet

        return super()._parse(resource_data)
