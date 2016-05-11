from texttable import Texttable

from ..formatters import to_format


def render_text_table(sheet, _, write_title):
    content = ""
    if write_title:
        content += "%s:\n" % sheet.name
    table = Texttable(max_width=0)
    data = sheet.to_array()
    table.set_cols_dtype(['t'] * len(data[0]))
    if len(sheet.colnames) > 0:
        table.set_chars(['-', '|', '+', '='])
        table.header(list(_cleanse_a_row(data[0])))
    else:
        table.add_row(list(_cleanse_a_row(data[0])))
    for sub_array in data[1:]:
        new_array = _cleanse_a_row(sub_array)
        table.add_row(list(new_array))
    content += table.draw()
    return content


def _cleanse_a_row(row):
    for item in row:
        if item == "":
            yield(" ")
        else:
            yield(to_format(str, item))


file_types = ('texttable',)
renderer = (render_text_table, None)