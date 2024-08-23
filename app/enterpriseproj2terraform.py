from .resource2terraform import Resource2Terraform


class EnterpriseProj2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(
            template_name='enterpriseproj',
            key_attr='project')
        self._attr_clean = {
            'project': 'name'
        }
