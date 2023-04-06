from pprint import pprint  # noqa: F401

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from .ecs2terraform import Ecs2Terraform
from .utils import load_metadata, load_sheet_data

LLD_FILENAME = 'LLD.xlsx'
METADATA_FILENAME = 'metadata.xlsx'


def process_ecs(worksheet: Worksheet):
    data = load_sheet_data(worksheet)

    ecs_handler = Ecs2Terraform()

    for row, ecs_data in data.items():
        error = ecs_handler.add_ecs(ecs_data)
        if error is not None:
            print(f'[ERR] Row {row}: {error}')
            exit()

    ecs_handler.output_terraform_code()


def main():
    metadata = load_metadata(METADATA_FILENAME)
    workbook = load_workbook(LLD_FILENAME, data_only=True)

    process_ecs(workbook[metadata['ecs_sheet']])


if __name__ == '__main__':
    main()
