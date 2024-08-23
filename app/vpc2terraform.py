from .resource2terraform import Resource2Terraform


class Vpc2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='vpc', key_attr='vpc')
        self._attr_clean = {
            'vpc': 'vpc_name',
            'project': 'enterprise_project'
        }
