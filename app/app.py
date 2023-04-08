from pprint import pprint  # noqa: F401

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from .ecs2terraform import Ecs2Terraform
from .utils import load_metadata, load_sheet_data
from .vpc2terraform import Vpc2Terraform

LLD_FILENAME = 'LLD.xlsx'
METADATA_FILENAME = 'metadata.xlsx'


def process_ecs(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    ecs_handler = Ecs2Terraform()

    for row, ecs_data in data.items():
        error = ecs_handler.add_ecs(ecs_data)
        if error is not None:
            print(f'[ERR] {worksheet.title}, row {row}: {error}')
            exit()

    with open('tf/ecs.tf', 'w') as output_file:
        ecs_handler.output_terraform_code(output_file)


def process_vpc(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    vpc_handler = Vpc2Terraform()

    for row, vpc_data in data.items():
        error = vpc_handler.add_vpc(vpc_data)
        if error is not None:
            print(f'[ERR] {worksheet.title}, row {row}: {error}')
            exit()

    with open('tf/vpc.tf', 'w') as output_file:
        vpc_handler.output_terraform_code(output_file)


def main():
    metadata = load_metadata(METADATA_FILENAME)
    workbook = load_workbook(LLD_FILENAME, data_only=True)

    process_ecs(workbook[metadata['ecs_sheet']])

    process_vpc(workbook[metadata['vpc_sheet']])


if __name__ == '__main__':
    main()
