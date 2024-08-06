from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Nat2Terraform:
    def __init__(self) -> None:
        self._nat = {}

    def to_dict(self) -> dict:
        return self._nat

    def append(self, nat_data: dict):
        if 'enterprise_project' in nat_data:
            nat_data['project'] = clean_str(nat_data['enterprise_project'])

        nat_id = clean_str(nat_data['nat_name'])

        vpc = clean_str(nat_data['vpc_name'])
        subnet = clean_str(nat_data['subnet_name'])
        nat_data['vpc'] = vpc
        nat_data['subnet'] = f'{vpc}_{subnet}'

        nat_data['nat'] = nat_id
        if nat_id in self._nat:
            return f'duplicate nat name ({nat_data["nat_name"]})'
        self._nat[nat_id] = nat_data

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all NAT data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for nat_data in self._nat.values():
            tf_code = renderer.render_name('templates/nat', nat_data)
            tf_code += '\n'
            output_file.write(tf_code)
