import re

from pystache import Renderer

from app.utils import clean_str


class Nics2Terraform:
    # Each ECS can have up to 8 NICs
    NIC_IDS = range(1, 9)

    # Mandatory parameters for a NIC
    NIC_PARAMS = ['vpc', 'subnet', 'fixed_ip', 'security_group']

    def __init__(self):
        self.ecs_nics = {}
        self.ecs_servergroup = {}

        # Example virtual_ips data:
        # {
        #     '10.1.0.10': {
        #         'hosts': ['srv01', 'srv02'],
        #         'ip': '10.1.0.10',
        #         'name': '10_1_0_10',
        #         'subnet': 'prod-1',
        #         'extension': True
        #     }
        # }
        # If 'extension' is present and is True in VIP data, it means it is
        # attached to an extension NIC (not the primary NIC).
        self.virtual_ips = {}

        # key is the original IP, value is the VIP
        self.ips_with_vips = {}

    def add_nics(self, ecs_data: dict):
        self.ecs_nics[ecs_data['ecs_name']] = []
        for i_nic in self.NIC_IDS:
            self._add_nic(ecs_data, i_nic)
            self._add_virtual_ip(ecs_data, i_nic)

    def add_servergroup_deps(self, server_groups: dict):
        for group_name, ecs_list in server_groups.items():
            for ecs_name in ecs_list:
                self.ecs_servergroup[ecs_name] = group_name

    def _add_nic(self, ecs_data: dict, i_nic: int):
        nic_data = {
            'ecs_name': ecs_data['ecs_name']
        }

        params = [f'nic{ i_nic }_{p}' for p in self.NIC_PARAMS]

        present_params = [p for p in params if p in ecs_data]
        missing_params = set(params) - set(present_params)

        # if fixed IP is missing for NIC i means there's no NIC
        if f'nic{ i_nic }_fixed_ip' not in present_params:
            return

        # if there are some params missing, throw an error
        if len(missing_params) != 0:
            msg = f'ecs {ecs_data["hostname"]} nic{i_nic} '
            msg += f'has missing params: {list(missing_params)[0]}'
            raise ValueError(msg)

        # nic1 params are already set inside ECS resource block
        if i_nic == 1:
            return

        # extract NIC_i params from ECS data
        for nic_param, ecs_param in zip(self.NIC_PARAMS, params):
            nic_data[nic_param] = ecs_data[ecs_param]

        self.ecs_nics[ecs_data['ecs_name']].append(nic_data)

    def _add_virtual_ip(self, ecs_data, i_nic):
        nic_vip_key = f'nic{ i_nic }_virtual_ip'
        nic_fixed_ip_key = f'nic{ i_nic }_fixed_ip'
        if nic_vip_key not in ecs_data:
            return

        # handle multiple VIPs (separated by line breaks) for the same NICs
        vip_addrs = ecs_data[nic_vip_key].split('\n')

        for vip_addr in vip_addrs:
            # remove IP comments, enclosed in parenthesis
            vip_addr = re.sub(r'\(.*\)', '', vip_addr).strip()

            if vip_addr not in self.virtual_ips:
                # first NIC with that VIP assigned
                self.virtual_ips[vip_addr] = {
                    'name': clean_str(vip_addr),
                    'subnet': ecs_data[f'nic{ i_nic }_subnet'],
                    'ip': vip_addr,
                    'hosts': [],
                    'extension': i_nic != 1
                }

            self.virtual_ips[vip_addr]['hosts'].append(ecs_data['ecs_name'])
            self.ips_with_vips[ecs_data[nic_fixed_ip_key]] = vip_addr

    def _nics_to_tfcode(self, ecs_name, renderer):
        tf_code = ''
        next_depends_on = None

        for nic_data in self.ecs_nics[ecs_name]:
            if next_depends_on is None:
                # first nic attachment depends on servergroup
                # join to be complete, otherwise joining_server_group
                # error happens when attaching nic
                if ecs_name in self.ecs_servergroup:
                    res = 'huaweicloud_compute_servergroup.servergroup_'
                    res += self.ecs_servergroup[ecs_name]
                    nic_data['depends_on'] = res
            else:
                # one attachment depends on the previous one to be
                # finished, in order to ensure disk order
                res = 'huaweicloud_compute_interface_attach.'
                res += f'nic_{ next_depends_on }'
                nic_data['depends_on'] = res

            # Source/Destination Check must be disabled
            # for NICs with virtual IPs assigned
            nic_has_vip = self.has_vip(nic_data['fixed_ip'])
            nic_data['source_dest_check'] = str(not nic_has_vip).lower()

            tf_code += renderer.render_name('templates/nic', nic_data)
            tf_code += '\n'

            next_depends_on = f"{ nic_data['ecs_name'] }_"
            next_depends_on += f"{ nic_data['subnet'] }"

        return tf_code

    def _vips_to_tfcode(self, renderer) -> str:
        tf_code = ''

        for vip_data in self.virtual_ips.values():
            ports = []
            for host in vip_data['hosts']:
                host = clean_str(host)
                if vip_data.get('extension', False):
                    # if VIP is for an extension NIC, use Terraform's split()
                    # to get the port ID from the interface_attach ID,
                    # which has the format "{ECS ID}/{Port ID}"
                    port_str = 'split("/", '
                    port_str += 'huaweicloud_compute_interface_attach'
                    port_str += f'.nic_{ host }_{ vip_data["subnet"] }'
                    port_str += '.id)[1]'
                else:
                    # if VIP is for the primary NIC, get the port ID from
                    # ECS' network block
                    port_str = f'huaweicloud_compute_instance.{host}'
                    port_str += '.network[0].port'

                ports.append(port_str)

            # transform array into string and preserve tf_code indentation
            vip_data['ports'] = ',\n    '.join(ports)

            tf_code += renderer.render_name('templates/vip', vip_data)
            tf_code += '\n'

        return tf_code

    def has_vip(self, fixed_ip: str) -> bool:
        return fixed_ip in self.ips_with_vips

    def terraform_code(self):
        renderer = Renderer()
        tf_code = ''

        for ecs_name in self.ecs_nics.keys():
            tf_code += self._nics_to_tfcode(ecs_name, renderer)

        tf_code += self._vips_to_tfcode(renderer)

        return tf_code
