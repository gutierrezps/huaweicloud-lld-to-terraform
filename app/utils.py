from typing import Any

from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.worksheet.worksheet import Worksheet


def clean_str(input_str: str) -> str:
    """Transform into lowercase and replace '-', '.' and ' ' with '_'"""
    ret = input_str.lower().replace('-', '_').replace('.', '_')
    ret = ret.replace(' ', '_')
    return ret


def cell_value(sheet: Worksheet, coord: str) -> Any:
    """Return cell value, whether it's merged or not.

    For example, if cells A1 and A2 are merged, the value is stored
    only in the first cell of the range (A1), and the other cells
    have an empty value.

    Using this function, the same value is returned for all cells in the
    merge range.

    Source: <https://stackoverflow.com/a/67610996/2014507>

    Args:
        sheet (Worksheet):
        coord (str): cell coordinate (e.g. 'A2')

    Raises:
        AssertionError: something is wrong with the spreadsheet

    Returns:
        Any: cell value, which can be date, str, int, float or None if
            it's empty
    """
    cell: Cell = sheet[coord]
    if not isinstance(cell, MergedCell):
        return cell.value

    # "Oh no, the cell is merged!"
    for range in sheet.merged_cells.ranges:
        if coord in range:
            return range.start_cell.value

    raise AssertionError('Merged cell is not in any merge range!')
