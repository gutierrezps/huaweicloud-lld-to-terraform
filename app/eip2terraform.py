from .resource2terraform import Resource2Terraform


class Eip2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='eip', key_attr='eip')

        self._attr_clean = {
            'project': 'enterprise_project',
            'eip': 'eip_name'
        }
