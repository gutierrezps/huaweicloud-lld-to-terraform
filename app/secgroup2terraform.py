from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Secgroup2Terraform:
    def __init__(self) -> None:
        self._secgroup = {}

    def add_secgroup_rule(self, rule_data: dict):
        secgroup = clean_str(rule_data['security_group_name'])

        if secgroup not in self._secgroup:
            self._secgroup[secgroup] = {
                'secgroup': secgroup,
                'secgroup_name': rule_data['security_group_name'],
                'region': rule_data['region'],
                'rules': []
            }

        if rule_data['protocol'] == 'all':
            del rule_data['protocol']
        if rule_data['ports'] == 'all':
            del rule_data['ports']

        self._secgroup[secgroup]['rules'].append(rule_data)

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all Secgroup data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for secgroup, secgroup_data in self._secgroup.items():
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
