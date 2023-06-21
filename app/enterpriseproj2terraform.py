from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class EnterpriseProj2Terraform:
    def __init__(self) -> None:
        self._projects = {}

    def add_project(self, project_data: dict):
        project = clean_str(project_data['name'])
        project_data['project'] = project
        self._projects[project] = project_data

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all Terraform data into Terraform code, and save
        to output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for data in self._projects.values():
            tf_code = renderer.render_name('templates/enterpriseproj', data)
            tf_code += '\n'
            output_file.write(tf_code)
