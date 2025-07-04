from io import TextIOWrapper
from pystache import Renderer

from .evs2terraform import Evs2Terraform
from .nic2terraform import Nic2Terraform
from .resource2terraform import Resource2Terraform


class Ecs2Terraform(Resource2Terraform):
    def __init__(self, last_wave: int):
        super().__init__(template_name='ecs', key_attr='ecs_name')
        self._servergroups = {}
        self._nics_handler = Nic2Terraform()
        self._evs_handler = Evs2Terraform()
        self._last_wave = last_wave

        self._attr_clean = {
            'ecs_name': 'hostname',
            'project': 'enterprise_project'
        }

        nic_clean_params = ['vpc', 'subnet', 'security_group']
        for i_nic in Nic2Terraform.NIC_IDS:
            params = [f'nic{ i_nic }_{p}' for p in nic_clean_params]
            for p in params:
                self._attr_clean[p] = p

    def _parse(self, resource_data: dict):
        for i_nic in Nic2Terraform.NIC_IDS:
            try:
                subnet_name = resource_data[f'nic{ i_nic }_vpc']
                subnet_name += '_' + resource_data[f'nic{ i_nic }_subnet']
                resource_data[f'nic{ i_nic }_subnet'] = subnet_name
            except KeyError:
                # nic is not defined
                pass

        tag_key = resource_data.pop('tag_key', None)
        if tag_key is not None:
            resource_data['tag'] = {
                'key': tag_key,
                'value': resource_data['tag_value']
            }

        group = resource_data.get('ecs_group', None)
        dedicated_host = resource_data.pop('dedicated_host', None)
        if group is not None or dedicated_host is not None:
            tenancy = 'dedicated' if dedicated_host == 'yes' else None
            resource_data['scheduler_hints'] = {
                'group': group,
                'tenancy': tenancy
            }

        return resource_data

    def _validate_ecs(self, ecs_data: dict):
        if ecs_data['ecs_name'] in self._resources_data:
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

    def add(self, resource_data: dict):
        resource_data = self._clean(resource_data)

        resource_data = self._parse(resource_data)

        error_msg = self._validate(resource_data)
        if error_msg is not None:
            return error_msg

        ecs_name = resource_data['ecs_name']

        # ECSs will be ignored if "Wave" value is not set, if it's
        # negative or if it's greather than "ECS last wave"
        # in metadata.xlsx
        ecs_wave = resource_data.pop('wave', 0)
        if ecs_wave <= 0 or ecs_wave > self._last_wave:
            return

        functions = [
            self._validate_ecs,
            self._nics_handler.add_nics,
            self._evs_handler.add,
            self._add_servergroup,
        ]

        for fn in functions:
            error = fn(resource_data)
            if error is not None:
                return error + f' ({resource_data["hostname"]})'

        nic1_has_vip = self._nics_handler.has_vip(
            resource_data['nic1_fixed_ip'])
        resource_data['source_dest_check'] = str(not nic1_has_vip).lower()

        secgroups = [resource_data['nic1_security_group']]
        secgroups.extend(self._nics_handler.get_secgroups(ecs_name))
        resource_data['security_groups'] = secgroups

        self._resources_data[ecs_name] = resource_data

        return None

    def _servergroups_to_terraform(self, output_file: TextIOWrapper):
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
        """
        renderer = Renderer()

        for data in self._servergroups.values():
            tf_code = renderer.render_name('templates/servergroup', data)
            tf_code += '\n'
            output_file.write(tf_code)

    def to_terraform(self, output_file: TextIOWrapper):
        """Transforms all ECS data into Terraform code, and save to
        tf/ecs.tf.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()

        for ecs_data in self._resources_data.values():
            secgroups = [
                f'huaweicloud_networking_secgroup.{secgroup}.id'
                for secgroup in ecs_data['security_groups']
            ]
            ecs_data['security_groups'] = ',\n    '.join(secgroups)
            tf_code = renderer.render_name('templates/ecs', ecs_data)
            tf_code += '\n'
            output_file.write(tf_code)

        self._servergroups_to_terraform(output_file)

        self._nics_handler.to_terraform(output_file)

        self._evs_handler.to_terraform(output_file)
