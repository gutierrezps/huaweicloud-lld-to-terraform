from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Eip2Terraform:
    def __init__(self) -> None:
        self._eip = {}

    def add_eip(self, eip_data: dict):
        if 'enterprise_project' in eip_data:
            eip_data['project'] = clean_str(eip_data['enterprise_project'])

        eip_id = clean_str(eip_data['eip_name'])
        eip_data['eip'] = eip_id
        if eip_id in self._eip:
            return f'duplicate eip name ({eip_data["eip_name"]})'
        self._eip[eip_id] = eip_data

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all EIP data into Terraform code, and save to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for eip_data in self._eip.values():
            tf_code = renderer.render_name('templates/eip', eip_data)
            tf_code += '\n'
            output_file.write(tf_code)
