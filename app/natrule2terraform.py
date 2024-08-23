import re

from .resource2terraform import Resource2Terraform
from .utils import clean_str


class NatRule2Terraform(Resource2Terraform):
    def __init__(self, nat_data: dict) -> None:
        super().__init__(template_name='nat-rule', key_attr='_id')

        self._attr_clean = {
            'nat': 'nat_name',
            'subnet': 'dnat_subnet_name',
            'eip': 'eip_name',
            'rule_type': 'rule_type'
        }

        self._nat_data = nat_data
        self._next_id = 1

    def _parse(self, rule_data: dict):
        rule_type = rule_data['rule_type']

        rule_data['template_variation'] = rule_type

        subnet = self._nat_data[rule_data['nat']]['vpc'] + '_'

        if rule_type == 'dnat':
            subnet += clean_str(rule_data['dnat_subnet_name'])
        else:
            dest = rule_data['snat_cidr_subnet'].strip()

            if re.match(r'(\d{1,3}\.){3}\d{1,3}\/\d{1,2}', dest) is not None:
                rule_data['cidr'] = dest
            else:
                subnet += clean_str(dest)

        rule_data['subnet'] = subnet

        rule_data['_id'] = self._next_id
        rule_data['rule'] = f'{rule_type}_rule{self._next_id:02}'

        self._next_id += 1

        return super()._parse(rule_data)

    def _validate(self, rule_data: dict):
        error_msg = None

        rule_type = rule_data['rule_type']
        if rule_type not in ['dnat', 'snat']:
            error_msg = f'Rule Type must be DNAT or SNAT ({rule_type})'

        return super()._validate(rule_data, error_msg)
