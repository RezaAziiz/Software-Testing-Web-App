import xlsxwriter
import os
from utilities.utils import check_folder
from utilities.imageutil import resize


def create_excel_data(file_name: str, title: str, listColumn: object, listKey: object, listData: object, listImageKey: list = []):
    check_folder('excel_report')
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('excel_report/'+file_name+".xlsx")
    worksheet = workbook.add_worksheet()

    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0
    # set formating
    column_format = workbook.add_format({'bold': True})
    title_format = workbook.add_format({'bold': True, 'font_size' : 20})

    # set title
    worksheet.write(row, col, title, title_format)
    row += 1

    # Iterate over the data and write it out row by row.
    # write column name
    for item, width in (listColumn):
        # set width
        worksheet.set_column(col, col, width)
        worksheet.write(row, col, item, column_format)
        col += 1
    row += 1
    # write Data
    for index in range(len(listData)):
        col = 0
        for key in (listKey):
            text = listData[index][key]
            if key not in listImageKey or text is None or text == '':
                worksheet.write(row, col, text)
            else:
                file_path = 'file_uploaded/'+text
                if os.path.exists(file_path):
                    # https://stackoverflow.com/questions/66776526/scale-images-in-a-readable-manner-in-xlsxwriter

                    # update worksheet
                    wrap = workbook.add_format({'text_wrap': True})
                    # worksheet.set_column(0, 4, 27.5, wrap)
                    worksheet.set_row(row, 150, wrap)

                    # resize image
                    image_buffer, image = resize(
                        file_path, (512, 512), format='JPEG')

                    data = {'x_offset': 10,
                            'x_scale': 200 / image.width,
                            'y_scale': 200 / image.height,
                            'object_position': 1}

                    # insert image
                    worksheet.insert_image(row, col, file_path, {
                                           'image_data': image_buffer, **data})
                else:
                    worksheet.write(row, col, text)
            col += 1
        row += 1
    row += 1

    workbook.close()


def create_excel_file(file_name: str):
    check_folder('excel_report')
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('excel_report/'+file_name+".xlsx")

    return workbook