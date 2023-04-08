from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Subnet2Terraform:
    def __init__(self) -> None:
        self._subnets = {}

    def add_subnet(self, subnet_data: dict):
        subnet = clean_str(subnet_data['subnet_name'])
        vpc = clean_str(subnet_data['vpc_name'])
        subnet_data['vpc'] = vpc
        subnet_data['subnet'] = f'{vpc}_{subnet}'
        if subnet in self._subnets:
            return f'duplicate subnet name ({subnet_data["subnet_name"]})'
        self._subnets[subnet] = subnet_data

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all Subnet data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for subnet_data in self._subnets.values():
            tf_code = renderer.render_name('templates/subnet', subnet_data)
            tf_code += '\n'
            output_file.write(tf_code)
