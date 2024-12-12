from io import TextIOWrapper
from pystache import Renderer

from .resource2terraform import Resource2Terraform


class Evs2Terraform(Resource2Terraform):
    # each ECS has at most 23 data disks
    DATA_DISK_IDS = range(1, 24)
    DISK_PARAMS = ['type', 'size', 'shared']

    def __init__(self) -> None:
        super().__init__(template_name='evs', key_attr='evs_name')
        self._ecs_attachments: dict[str, list] = {}

    def add(self, ecs_data: dict):
        ecs_disks = {}

        for i_disk in self.DATA_DISK_IDS:
            evs_data = self._parse(ecs_data, i_disk)
            if evs_data is None:
                break

            error_msg = self._validate(evs_data)
            if error_msg is not None:
                return error_msg

            ecs_disks[i_disk] = evs_data

        if not ecs_disks:
            return None

        self._ecs_attachments[ecs_data['ecs_name']] = []

        for i_disk, evs_data in ecs_disks.items():
            evs = self._consolidate_evs_data(ecs_data, evs_data, i_disk)
            if evs['evs_name'] not in self._resources_data:
                self._resources_data[evs['evs_name']] = evs
            self._ecs_attachments[ecs_data['ecs_name']].append(evs)

    def _validate(self, disk_data: dict):
        error_msg = None
        i_disk = disk_data['i_disk']

        disk_size = disk_data.get('size', 0)
        if disk_size < 10:
            msg = f'data disk {i_disk} size < 10GB ({disk_size})'
            raise ValueError(msg)

        # type, size and shared should be specified for each data disk,
        # check if there is any of those values missing
        missing_params = set(self.DISK_PARAMS)
        missing_params -= set(disk_data.keys())
        if missing_params:
            msg = f'data disk {i_disk} has missing params: '
            msg += f'{list(missing_params)[0]}'
            raise ValueError(msg)

        return error_msg

    def _parse(self, ecs_data: dict, i_disk: int):
        evs_data = {}

        # extract values for each param
        for param in self.DISK_PARAMS:
            full_param = f'data_disk_{i_disk}_{param}'
            if full_param in ecs_data:
                if param == 'shared':
                    # convert 'shared' disk value to boolean
                    is_shared = ecs_data[full_param].lower() == 'yes'
                    ecs_data[full_param] = is_shared
                evs_data[param] = ecs_data[full_param]

        if not evs_data:
            return None

        evs_data['i_disk'] = i_disk
        return evs_data

    def _consolidate_evs_data(
            self, ecs_data: dict, evs_data: dict, i_disk: int
            ):
        is_shared = evs_data['shared']

        evs_data['device_type'] = 'VBD'
        evs_name = ecs_data['ecs_name']
        if is_shared:
            # ecs_name is expected to be the same for ECSs sharing the
            # same data, except for the last letter (e.g. srv01a, srv01b),
            # so evs_name will contain the ecs_name minus the last
            # letter for shared EVSs (e.g. srv01)
            evs_name = ecs_data['ecs_name'][:-1]

            # SCSI device type is recommended for shared disks
            evs_data['device_type'] = 'SCSI'

        evs_name = f'{evs_name}_data_{i_disk}'
        evs_name += '_shared' if is_shared else ''

        evs_data['evs_name'] = evs_name
        device = '/dev/vd' + chr(ord('a') + i_disk)
        evs_data['evs_device'] = device

        COPY_PARAMS_MANDATORY = ['ecs_name', 'region', 'az']
        for param in COPY_PARAMS_MANDATORY:
            evs_data[param] = ecs_data[param]

        COPY_PARAMS_OPTIONAL = ['tag', 'project']
        for param in COPY_PARAMS_OPTIONAL:
            if param in ecs_data:
                evs_data[param] = ecs_data[param]

        # Terraform bool is all lowercase
        evs_data['shared'] = str(is_shared).lower()

        return evs_data

    def _attachments_to_tfcode(self) -> str:
        renderer = Renderer()
        tf_code = ''

        for ecs_name, disk_list in self._ecs_attachments.items():
            next_depends_on = None
            for evs_data in disk_list:
                if next_depends_on is not None:
                    # one attachment depends on the previous one to be
                    # finished, in order to ensure disk order
                    res = 'huaweicloud_compute_volume_attach.'
                    res += f'evs_{next_depends_on}_attachment'
                    evs_data['depends_on'] = res

                shared_letter = ''
                if evs_data['shared'] == 'true':
                    shared_letter = evs_data['ecs_name'][-1]
                evs_data['shared_letter'] = shared_letter

                tf_code += renderer.render_name(
                    'templates/evs-attach', evs_data)
                tf_code += '\n'
                next_depends_on = evs_data['evs_name']
                next_depends_on += shared_letter

        return tf_code

    def to_terraform(self, output_file: TextIOWrapper):
        super().to_terraform(output_file)
        tf_code = self._attachments_to_tfcode()
        output_file.write(tf_code)
