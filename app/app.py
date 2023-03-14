import re
from pprint import pprint  # noqa: F401

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell import Cell
from pystache import Renderer
from tqdm import tqdm

from app.evs2terraform import Evs2Terraform
from app.nics2terraform import Nics2Terraform
from app.utils import cell_value, clean_str

LLD_FILENAME = 'LLD.xlsx'
METADATA_FILENAME = 'metadata.xlsx'


def load_metadata() -> dict:
    """Load parameters set on metadata.xlsx, which tells where to
    look for information in the LLD spreadsheet.

    Returns:
        dict: key is the environment id (env01, env02 etc), value is a
            dict with each param and its value. If cell is empty,
            the parameter will not be present in the environment.
    """
    wb = load_workbook(METADATA_FILENAME)
    worksheet: Worksheet = wb['envs']

    # key: environment ID, value: dict with params and values
    envs = {}

    env_sequence = []

    # read all environment IDs (B1, C1, D1, ...)
    for row in worksheet.iter_rows(min_row=1, max_row=1, min_col=2):
        for cell in row:
            envs[cell.value] = {}
            env_sequence.append(cell.value)

    # read parameters of each environment, from row 2 onward
    for row in worksheet.iter_rows(min_row=2, min_col=1):
        param = None

        for col, cell in enumerate(row):
            if param is None:
                # first column is the parameter name
                param = cell.value
                continue

            envs[env_sequence[col-1]][param] = cell.value

    return envs


def load_lld_columns(workbook: Workbook, envs: dict) -> dict:
    for env, metadata in envs.items():
        sheet = metadata['sheet']
        worksheet = workbook[sheet]
        columns = {}
        for col in worksheet.iter_cols(min_col=1, min_row=1, max_row=1):
            header: Cell = col[0]

            param = clean_str(header.value) + '_col'
            if param in columns:
                msg = f'[ERR] Duplicate header in sheet {sheet} '
                msg += f'({param})'
                print(msg)
                exit(-1)

            columns[param] = header.column_letter

        envs[env].update(columns)

    return envs


def load_ecs(workbook: Workbook, env_params: dict) -> dict:
    """Load ECS specs from Workbook, for the given environment.

    ECS specs/parameters are located using ecs_*_col params in the
    environment params. So, if env['ecs_flavor_col'] = 'H' for example,
    data in column 'H' will be loaded to 'flavor' in the ECS specs.

    Args:
        workbook (Workbook): LLD workbook
        env_params (dict): environment parameters

    Raises:
        ValueError: if there's an ECS with duplicate name

    Returns:
        dict: key is the ecs_name, values are the ECS specs
    """
    worksheet = workbook[env_params['sheet']]

    params_cols = {}
    for param in env_params.keys():
        # ignore params that are not in the "*_col" format
        if re.match(r'.*_col', param) is None:
            continue

        # strip "_col"
        p = param.replace('_col', '')
        params_cols[p] = env_params[param]

    # Key is ecs_name, value is dict with params and their values. E.g.:
    # ecs_list['srv01'] = {'flavor': 's3.large.2', 'az': ..., ...}
    ecs_list = {}

    row_range = range(env_params['range_start'], env_params['range_end']+1)

    for row in tqdm(row_range, desc='Reading LLD'):
        hostname = worksheet[params_cols['hostname'] + str(row)].value
        ecs_name = clean_str(hostname)
        if ecs_name in ecs_list:
            msg = f'[ERR] Duplicate ECS hostname in {env_params["name"]} '
            msg += f' environment ({hostname})'
            raise ValueError(msg)

        ecs_list[ecs_name] = {'ecs_name': ecs_name}
        for param, col in params_cols.items():
            # Ignore ECS params that do not have a column assigned for
            # the environment. For example, Test environments do not
            # have ECS groups, so there's no column assigned
            if col is None:
                continue

            val = cell_value(worksheet, col + str(row))

            # params that are not set for the given ECS (empty cell) are
            # not saved to ecs_list[ecs_name]
            if val is not None:
                ecs_list[ecs_name][param] = val

    return ecs_list


def update_ecs_data(ecs_data: dict, env_id: str) -> dict:
    """Updates the ECS data with information based on the environment,
    and also apply transformations.

    Args:
        ecs_data (dict): input ECS params
        env_id (str): environment ID

    Returns:
        dict: ECS params updated
    """
    ecs_data['security_group'] = clean_str(ecs_data['security_group'])

    for i_nic in Nics2Terraform.NIC_IDS:
        # clean up subnet name
        key = f'nic{i_nic}_subnet'
        if key in ecs_data:
            ecs_data[key] = clean_str(ecs_data[key])

    return ecs_data


def server_groups_to_tfcode(server_groups: dict) -> str:
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

    for group_name, ecs_names in server_groups.items():
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


def save_ecs_as_terraform(all_ecs: dict, env_id: str):
    """Transforms all ECS data into Terraform code, and save to
    tf/{ env_id }.tf.

    Args:
        all_ecs (dict): All ECS data
        env_id (str): environment ID
    """

    renderer = Renderer()
    tf_file = open(f'tf/{ env_id }.tf', 'w')

    server_groups = {}

    evs_handler = Evs2Terraform()
    nics_handler = Nics2Terraform()

    for ecs_name, ecs_data in all_ecs.items():
        ecs_data = update_ecs_data(ecs_data, env_id)

        evs_handler.add_disks(ecs_data)
        nics_handler.add_nics(ecs_data)

        primary_nic_has_vip = nics_handler.has_vip(ecs_data['nic1_static_ip'])
        ecs_data['source_dest_check'] = str(not primary_nic_has_vip).lower()

        tf_code = renderer.render_name('templates/ecs', ecs_data)
        tf_code += '\n'

        if 'group' in ecs_data:
            if ecs_data['group'] not in server_groups:
                server_groups[ecs_data['group']] = []
            server_groups[ecs_data['group']].append(ecs_name)

        # write Terraform code for current ECS
        tf_file.write(tf_code)

    tf_file.write(server_groups_to_tfcode(server_groups))

    nics_handler.add_servergroup_deps(server_groups)
    tf_file.write(nics_handler.terraform_code())

    evs_handler.add_servergroup_deps(server_groups)
    tf_file.write(evs_handler.terraform_code())

    tf_file.close()


def main():
    envs = load_metadata()

    wb = load_workbook(LLD_FILENAME, data_only=True)

    envs = load_lld_columns(wb, envs)

    for env in envs.keys():
        ecs = load_ecs(wb, envs[env])
        save_ecs_as_terraform(ecs, env)


if __name__ == '__main__':
    main()
