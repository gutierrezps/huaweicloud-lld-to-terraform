from .resource2terraform import Resource2Terraform


class Subnet2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='subnet', key_attr='subnet')
        self._attr_clean = {
            'subnet': 'subnet_name',
            'vpc': 'vpc_name'
        }

    def _parse(self, subnet_data: dict):
        subnet = f"{subnet_data['vpc']}_{subnet_data['subnet']}"
        subnet_data['subnet'] = subnet

        return super()._parse(subnet_data)
