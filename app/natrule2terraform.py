import re
from io import TextIOWrapper

from pystache import Renderer

from .utils import clean_str


class NatRule2Terraform:
    def __init__(self, nat_data: dict) -> None:
        self._nat_rule = []
        self._nat_data = nat_data

    def append(self, rule_data: dict):
        rule_data['rule_type'] = rule_data['rule_type'].lower()
        rule_type = rule_data['rule_type']

        if rule_type not in ['dnat', 'snat']:
            return 'Rule Type must be DNAT or SNAT'

        nat = clean_str(rule_data['nat_name'])
        rule_data['nat'] = nat

        subnet = self._nat_data[nat]['vpc'] + '_'

        if rule_type == 'dnat':
            subnet += clean_str(rule_data['dnat_subnet_name'])
            rule_data['subnet'] = subnet
        else:
            dest = rule_data['snat_cidr_subnet'].strip()

            if re.match(r'(\d{1,3}\.){3}\d{1,3}\/\d{1,2}', dest) is not None:
                rule_data['cidr'] = dest
            else:
                subnet += clean_str(dest)
                rule_data['subnet'] = subnet

        eip = clean_str(rule_data['eip_name'])
        rule_data['eip'] = eip

        self._nat_rule.append(rule_data)

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all NAT rules data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for i, nat_data in enumerate(self._nat_rule):
            filename = f'nat-rule-{nat_data["rule_type"]}'
            nat_data['rule'] = f'{nat_data["rule_type"]}_rule{i+1:02}'
            tf_code = renderer.render_name(f'templates/{filename}', nat_data)
            tf_code += '\n'
            output_file.write(tf_code)
