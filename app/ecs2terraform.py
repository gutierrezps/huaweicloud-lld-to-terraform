from pystache import Renderer

from .evs2terraform import Evs2Terraform
from .nics2terraform import Nics2Terraform
from .utils import clean_str


class Ecs2Terraform:
    def __init__(self):
        self._ecs = {}
        self._server_groups = {}
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
        return ecs_data

    def _validate_ecs(self, ecs_data: dict):
        if ecs_data['ecs_name'] in self._ecs:
            return 'duplicate hostname'

        if ecs_data['system_disk_size'] < 40:
            return 'system disk < 40'

        return None

    def _add_server_group(self, ecs_data: dict):
        ecs_group = ecs_data.get('ecs_group', None)

        if ecs_group is None:
            return None

        if ecs_group not in self._server_groups:
            self._server_groups[ecs_group] = []

        self._server_groups[ecs_group].append(ecs_data['ecs_name'])

        return None

    def add_ecs(self, ecs_data: dict):
        ecs_name = clean_str(ecs_data['hostname'])
        ecs_data['ecs_name'] = ecs_name

        ecs_data = self._transform_params(ecs_data)

        functions = [
            self._validate_ecs,
            self._nics_handler.add_nics,
            self._evs_handler.add_disks,
            self._add_server_group,
        ]

        for fn in functions:
            error = fn(ecs_data)
            if error is not None:
                return error + f' ({ecs_data["hostname"]})'

        nic1_has_vip = self._nics_handler.has_vip(ecs_data['nic1_fixed_ip'])
        ecs_data['source_dest_check'] = str(not nic1_has_vip).lower()

        self._ecs[ecs_name] = ecs_data

        return None

    def _server_groups_to_tfcode(self):
        """Transforms server Groups to Terraform code.

        Example input data:

        {
            'group_name': ['srv01', 'srv02']
        }

        Args:
            server_groups (dict): key is the group name, and value is the
                list of ecs_names

        Returns:
            str: Terraform code for all server groups
        """
        tf_code = ''
        renderer = Renderer()

        for group_name, ecs_names in self._server_groups.items():
            data = {'name': group_name}

            members = [
                    f'huaweicloud_compute_instance.{name}.id'
                    for name in ecs_names
                ]

            # transform array into string and preserve tf_code indentation
            data['members'] = ',\n    '.join(members)

            tf_code += renderer.render_name('templates/server_group', data)
            tf_code += '\n'

        return tf_code

    def output_terraform_code(self):
        """Transforms all ECS data into Terraform code, and save to
        tf/ecs.tf.
        """
        renderer = Renderer()

        tf_file = open('tf/ecs.tf', 'w')

        for ecs_data in self._ecs.values():
            tf_code = renderer.render_name('templates/ecs', ecs_data)
            tf_code += '\n'
            tf_file.write(tf_code)

        tf_file.write(self._server_groups_to_tfcode())

        self._nics_handler.add_servergroup_deps(self._server_groups)
        tf_file.write(self._nics_handler.terraform_code())

        self._evs_handler.add_servergroup_deps(self._server_groups)
        tf_file.write(self._evs_handler.terraform_code())

        tf_file.close()
