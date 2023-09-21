from pprint import pprint  # noqa: F401
from typing import Callable

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from .ecs2terraform import Ecs2Terraform
from .enterpriseproj2terraform import EnterpriseProj2Terraform
from .secgroup2terraform import Secgroup2Terraform
from .subnet2terraform import Subnet2Terraform
from .utils import load_metadata, load_sheet_data
from .vpc2terraform import Vpc2Terraform

LLD_FILENAME = 'LLD.xlsx'
METADATA_FILENAME = 'metadata.xlsx'


def process_sheet_data(
        sheet_title: str,
        sheet_data: list,
        handler_method: Callable
        ):
    for row_number, row_data in sheet_data.items():
        error = None
        try:
            error = handler_method(row_data)
        except KeyError as e:
            error = 'mandatory column "' + e.args[0] + '" not set'
        except ValueError as e:
            error = e.args[0]

        if error is not None:
            print(f'[ERR] Sheet "{sheet_title}", row {row_number}: {error}')
            exit()


def process_ecs(worksheet: Worksheet, last_wave: int):
    data = load_sheet_data(worksheet)

    ecs_handler = Ecs2Terraform(last_wave)

    process_sheet_data(worksheet.title, data, ecs_handler.add_ecs)

    with open('tf/ecs.tf', 'w') as output_file:
        ecs_handler.output_terraform_code(output_file)


def process_vpc(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    vpc_handler = Vpc2Terraform()

    process_sheet_data(worksheet.title, data, vpc_handler.add_vpc)

    with open('tf/vpc_subnet.tf', 'w') as output_file:
        vpc_handler.output_terraform_code(output_file)


def process_subnet(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    subnet_handler = Subnet2Terraform()

    process_sheet_data(worksheet.title, data, subnet_handler.add_subnet)

    with open('tf/vpc_subnet.tf', 'a') as output_file:
        subnet_handler.output_terraform_code(output_file)


def process_secgroup(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    secgroup_handler = Secgroup2Terraform()

    process_sheet_data(
        worksheet.title, data, secgroup_handler.add_secgroup_rule)

    with open('tf/secgroups.tf', 'w') as output_file:
        secgroup_handler.output_terraform_code(output_file)


def process_enterpriseproj(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    project_handler = EnterpriseProj2Terraform()

    process_sheet_data(
        worksheet.title, data, project_handler.add_project)

    with open('tf/enterpriseproj.tf', 'w') as output_file:
        project_handler.output_terraform_code(output_file)


def main():
    metadata = load_metadata(METADATA_FILENAME)
    workbook = load_workbook(LLD_FILENAME, data_only=True)

    # load and validate "ECS last wave"
    try:
        last_wave = int(metadata['ecs_last_wave'])
        assert last_wave > 0
    except (ValueError, AssertionError):
        print('[ERR] Invalid ECS last wave value (must be a number > 0)')

    process_ecs(workbook[metadata['ecs_sheet']], last_wave)

    process_vpc(workbook[metadata['vpc_sheet']])

    process_subnet(workbook[metadata['subnet_sheet']])

    process_secgroup(workbook[metadata['secgroup_sheet']])

    process_enterpriseproj(workbook[metadata['enterprise_proj_sheet']])


if __name__ == '__main__':
    main()
