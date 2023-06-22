from io import TextIOWrapper
from pystache import Renderer

from .evs2terraform import Evs2Terraform
from .nics2terraform import Nics2Terraform
from .utils import clean_str


class Ecs2Terraform:
    def __init__(self):
        self._ecs = {}
        self._servergroups = {}
        self._nics_handler = Nics2Terraform()
        self._evs_handler = Evs2Terraform()

    def _transform_params(self, ecs_data: dict) -> dict:
        """Apply transformations to the ecs parameters.

        Transformations include renaming, appending, clean_str etc.

        Args:
            ecs_data (dict): input ecs data

        Returns:
            dict: output ecs data
        """
        ecs_data = self._nics_handler.transform_params(ecs_data)

        tag_key = ecs_data.pop('tag_key', None)
        if tag_key is not None:
            ecs_data['tag'] = {
                'key': tag_key,
                'value': ecs_data['tag_value']
            }

        return ecs_data

    def _validate_ecs(self, ecs_data: dict):
        if ecs_data['ecs_name'] in self._ecs:
            return 'duplicate hostname'

        if ecs_data['system_disk_size'] < 40:
            return 'system disk < 40'

        return None

    def _add_servergroup(self, ecs_data: dict):
        ecs_group = ecs_data.get('ecs_group', None)

        if ecs_group is None:
            return

        if ecs_group not in self._servergroups:
            self._servergroups[ecs_group] = {
                'name': ecs_group,
                'region': ecs_data['region']
            }

    def add_ecs(self, ecs_data: dict):
        ecs_name = clean_str(ecs_data['hostname'])
        ecs_data['ecs_name'] = ecs_name

        if 'enterprise_project' in ecs_data:
            ecs_data['project'] = clean_str(ecs_data['enterprise_project'])

        ecs_data = self._transform_params(ecs_data)

        functions = [
            self._validate_ecs,
            self._nics_handler.add_nics,
            self._evs_handler.add_disks,
            self._add_servergroup,
        ]

        for fn in functions:
            error = fn(ecs_data)
            if error is not None:
                return error + f' ({ecs_data["hostname"]})'

        nic1_has_vip = self._nics_handler.has_vip(ecs_data['nic1_fixed_ip'])
        ecs_data['source_dest_check'] = str(not nic1_has_vip).lower()

        self._ecs[ecs_name] = ecs_data

        return None

    def _servergroups_to_tfcode(self):
        """Transforms server Groups to Terraform code.

        Example input data:

        {
            'group_name': {
                'name': 'group_name',
                'region': '...'
        }

        Args:
            servergroups (dict): key is the group name, and value is the
                list of ecs_names

        Returns:
            str: Terraform code for all server groups
        """
        tf_code = ''
        renderer = Renderer()

        for data in self._servergroups.values():
            tf_code += renderer.render_name('templates/servergroup', data)
            tf_code += '\n'

        return tf_code

    def output_terraform_code(self, output_file: TextIOWrapper):
        """Transforms all ECS data into Terraform code, and save to
        tf/ecs.tf.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for ecs_data in self._ecs.values():
            tf_code = renderer.render_name('templates/ecs', ecs_data)
            tf_code += '\n'
            output_file.write(tf_code)

        output_file.write(self._servergroups_to_tfcode())

        output_file.write(self._nics_handler.terraform_code())

        output_file.write(self._evs_handler.terraform_code())
