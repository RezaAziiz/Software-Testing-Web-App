from fpdf import FPDF
from utilities.utils import check_folder
import os


def create_pdf_data(file_name: str, title: str, listColumn: object, listKey: object, listData: object, listImageKey: list = []):
    check_folder("pdf_report")
    pdf = FPDF(orientation='L')
    pdf.add_page()
    # Set font
    pdf.set_font('Arial', 'B', 16)
    # Centered text in a framed 20*10 mm cell and line break
    # (width, height, text, border, ln, align:C,L,R )
    pdf.cell(20, 10, title, 0, 1, 'L')

    # Set Header
    # Set font
    pdf.set_font('Arial', 'B', 10)
    col_widths = tuple([col[1] for col in listColumn])
    with pdf.table(col_widths=col_widths) as table:
        row = table.row()
        for column, width in (listColumn):
            row.cell(str(column))

        # print(listKey)
        # Set Data
        # Set font
        pdf.set_font('Arial', '', 8)
        jml_rows = len(listData)
        for index_row in range(jml_rows):
            row = table.row()
            for key in (listKey):
                text = str(listData[index_row][key])

                if key not in listImageKey or text is None or text == '':
                    row.cell(text)
                else:
                    file_path = 'file_uploaded/'+text
                    if os.path.exists(file_path):
                        row.cell(img=file_path, img_fill_width=True)
                        # row.cell(img=file_path)
                    else:
                        row.cell(text)

    pdf.output(f'pdf_report/{file_name}.pdf', 'F')
