from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Vpc2Terraform:
    def __init__(self) -> None:
        self._vpc = {}

    def add_vpc(self, vpc_data: dict):
        if 'enterprise_project' in vpc_data:
            vpc_data['project'] = clean_str(vpc_data['enterprise_project'])

        vpc = clean_str(vpc_data['vpc_name'])
        vpc_data['vpc'] = vpc
        if vpc in self._vpc:
            return f'duplicate vpc name ({vpc_data["vpc_name"]})'
        self._vpc[vpc] = vpc_data

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all VPC data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for vpc_data in self._vpc.values():
            tf_code = renderer.render_name('templates/vpc', vpc_data)
            tf_code += '\n'
            output_file.write(tf_code)
