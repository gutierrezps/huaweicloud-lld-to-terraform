from pystache import Renderer


class Evs2Terraform:
    # each ECS has at most 23 data disks
    DATA_DISK_IDS = range(1, 24)
    DISK_PARAMS = ['type', 'size', 'shared']

    def __init__(self):
        self.current_ecs_disks = {}
        self.data_disks = {}
        self.ecs_attachments = {}

    def _extract_data_disk_params(self, ecs_data: dict, i_disk: int):
        self.current_ecs_disks[i_disk] = {}

        # extract values for each param
        for param in self.DISK_PARAMS:
            full_param = f'data_disk_{i_disk}_{param}'
            if full_param in ecs_data:
                if param == 'shared':
                    # convert 'shared' disk value to boolean
                    is_shared = ecs_data[full_param].lower() == 'yes'
                    ecs_data[full_param] = is_shared
                self.current_ecs_disks[i_disk][param] = ecs_data[full_param]

        # check if no data disk param was filled
        if not self.current_ecs_disks[i_disk]:
            self.current_ecs_disks.pop(i_disk)
            return

        disk_size = self.current_ecs_disks[i_disk].get('size', 0)
        if not disk_size:
            msg = f"[WRN] ignoring disk {i_disk} of {ecs_data['hostname']}"
            msg += ' - empty size'
            print(msg)
            self.current_ecs_disks.pop(i_disk)
            return

        if disk_size < 10:
            msg = f'ecs {ecs_data["hostname"]} data disk {i_disk} '
            msg += f'size < 10GB ({disk_size})'
            raise ValueError(msg)

        # type, size and shared should be specified for each data disk,
        # check if there is any of those values missing
        missing_params = set(self.DISK_PARAMS)
        missing_params -= set(self.current_ecs_disks[i_disk].keys())
        if missing_params:
            msg = f'ecs {ecs_data["hostname"]} data disk {i_disk} '
            msg += f'has missing params: {list(missing_params)[0]}'
            raise ValueError(msg)

    def _consolidate_evs_data(
            self, ecs_data: dict, evs_data: dict, i_disk: int
            ):
        is_shared = evs_data['shared']

        evs_name = ecs_data['ecs_name']
        if is_shared:
            # ecs_name is the same for ECSs sharing the same data,
            # except for the last letter (e.g. srv01a, srv01b),
            # so evs_name will be the ecs_name minus the last letter
            # for shared EVSs
            evs_name = ecs_data['ecs_name'][:-1]

        evs_name = f'{evs_name}_data_{i_disk}'
        evs_name += '_shared' if is_shared else ''

        evs_data['evs_name'] = evs_name
        device = '/dev/vd' + chr(ord('a') + i_disk)
        evs_data['evs_device'] = device

        COPY_PARAMS = ['ecs_name', 'region', 'az']
        for param in COPY_PARAMS:
            evs_data[param] = ecs_data[param]

        if 'project' in ecs_data:
            evs_data['project'] = ecs_data['project']

        # Terraform bool is all lowercase
        evs_data['shared'] = str(is_shared).lower()

        return evs_data

    def add_disks(self, ecs_data: dict):
        self.current_ecs_disks = {}

        for i_disk in self.DATA_DISK_IDS:
            self._extract_data_disk_params(ecs_data, i_disk)

        if not self.current_ecs_disks:
            return

        self.ecs_attachments[ecs_data['ecs_name']] = []

        for i_disk, evs_data in self.current_ecs_disks.items():
            evs = self._consolidate_evs_data(ecs_data, evs_data, i_disk)
            if evs['evs_name'] not in self.data_disks:
                self.data_disks[evs['evs_name']] = evs
            self.ecs_attachments[ecs_data['ecs_name']].append(evs)

    def _disks_to_tfcode(self) -> str:
        renderer = Renderer()
        tf_code = ''

        for evs_data in self.data_disks.values():
            tf_code += renderer.render_name('templates/evs', evs_data)
            tf_code += '\n'

        return tf_code

    def _attachments_to_tfcode(self) -> str:
        renderer = Renderer()
        tf_code = ''

        for ecs_name, disk_list in self.ecs_attachments.items():
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

    def terraform_code(self) -> str:
        tf_code = self._disks_to_tfcode()
        tf_code += self._attachments_to_tfcode()
        return tf_code
