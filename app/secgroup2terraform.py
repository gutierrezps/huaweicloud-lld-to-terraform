from io import TextIOWrapper

from pystache import Renderer

from .resource2terraform import Resource2Terraform


class Secgroup2Terraform(Resource2Terraform):
    def __init__(self) -> None:
        super().__init__(template_name='secgroup', key_attr='secgroup')
        self._attr_clean = {
            'secgroup': 'security_group_name',
            'project': 'enterprise_project'
        }

    def add(self, resource_data: dict):
        resource_data = self._clean(resource_data)
        secgroup = resource_data['secgroup']

        if secgroup not in self._resources_data:
            self._resources_data[secgroup] = {
                'secgroup': secgroup,
                'secgroup_name': resource_data['security_group_name'],
                'region': resource_data['region'],
                'rules': [],
                'project': resource_data['project']
            }

        if resource_data['protocol'] == 'all':
            del resource_data['protocol']
        if resource_data['ports'] == 'all':
            del resource_data['ports']

        self._resources_data[secgroup]['rules'].append(resource_data)

    def to_terraform(self, output_file: TextIOWrapper):
        """Transforms all Secgroup data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for secgroup, secgroup_data in self._resources_data.items():
            tf_code = renderer.render_name('templates/secgroup', secgroup_data)
            tf_code += '\n'
            output_file.write(tf_code)

            for i, rule in enumerate(secgroup_data['rules']):
                rule['rule'] = f'{secgroup}_rule{i+1:02}'
                rule['secgroup'] = secgroup
                tf_code = renderer.render_name(
                    'templates/secgroup_rule', rule)
                tf_code += '\n'
                output_file.write(tf_code)
