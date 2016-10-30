from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment
import datetime


def style_range(ws, cell_range, border=Border(), fill=None, font=None, alignment=None):
    top = Border(top=border.top)
    left = Border(left=border.left)
    right = Border(right=border.right)
    bottom = Border(bottom=border.bottom)

    first_cell = ws[cell_range.split(":")[0]]
    if alignment:
        ws.merge_cells(cell_range)
        first_cell.alignment = alignment

    rows = ws[cell_range]
    if font:
        first_cell.font = font

    for cell in rows[0]:
        cell.border += top
    for cell in rows[-1]:
        cell.border += bottom

    for row in rows:
        l = row[0]
        r = row[-1]
        l.border += left
        r.border += right
        if fill:
            for c in row:
                c.fill = fill


def example():
    wb = Workbook()
    # grab the active worksheet
    ws = wb.active
    # Data can be assigned directly to cells
    ws['A1'] = 42
    # Rows can also be appended
    ws.append([1, 2, 3])
    # Python types will automatically be converted
    ws['A2'] = datetime.datetime.now()
    # Save the file
    wb.save("example.xlsx")


def multiCell(ws, value, rng, b=False, color="000000", horizontal="center", vertical="center"):
    my_cell = ws[rng.split(":")[0]]
    my_cell.value = value
    font = Font(b=b, color=color)
    al = Alignment(horizontal=horizontal, vertical=vertical)
    style_range(ws, rng, font=font, alignment=al)


def export():
    wb = Workbook()
    ws = wb.active
    multiCell(ws, "Proj. No.", "A1:A2")
    multiCell(ws, "Title", "B1:B2")
    multiCell(ws, "Preference", "C1:E1")
    for i in range(3):
        cell = ws["%s2" % chr(ord('C') + i)]
        cell.value = i + 1
        cell.alignment = Alignment(horizontal="center", vertical="center")
    wb.save("test.xlsx")
    # TODO: the writing of excel data


if __name__ == "__main__":
    export()
