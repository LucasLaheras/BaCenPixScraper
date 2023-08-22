import pandas
import numpy


# function to save with highlight cells
def highlight_cells(val):
    try:
        color = 'yellow' if '-->' in val else 'white'
    except:
        color = 'white'
    return 'background-color: {}'.format(color)


def write_only_diferences(df1, df2, rows, cols):

    for item in zip(rows, cols):
        df2.iloc[item[0], item[1]] = " {} --> {} ".format(df2.iloc[item[0], item[1]], df1.iloc[item[0], item[1]])

    unique_rows = numpy.unique(rows)

    a = numpy.arange(df2.shape[0])
    a = numpy.delete(a, unique_rows)

    df = df2.drop(a[:])

    return df


# compare sheets
def sheet_is_equal(df1, df2):
    if df1.equals(df2):
        return True, None

    # IF SHAPE OF THESE FILES IS DIFFERENT IT WILL ADJUST
    if df1.shape[0] != df2.shape[0]:
        diff_shape = df1.shape[0] - df2.shape[0]
        if diff_shape > 0:
            df2 = df2._append(pandas.DataFrame(numpy.zeros((diff_shape, df1.shape[1])), columns=df1.columns.array[:]), ignore_index=True)
        else:
            df1 = df1._append(pandas.DataFrame(numpy.zeros((-diff_shape, df2.shape[1])), columns=df2.columns.array[:]), ignore_index=True)

    if df1.shape[1] != df2.shape[1]:
        df1 = df1._append(pandas.DataFrame(numpy.zeros((1, df2.shape[1])), columns=df2.columns.array[:]),
                              ignore_index=True)
        df2 = df2._append(pandas.DataFrame(numpy.zeros((1, df1.shape[1])), columns=df1.columns.array[:]),
                              ignore_index=True)

    df1 = df1.fillna(0)
    df2 = df2.fillna(0)

    # this will return a matrix of comparative
    compare_values = df1.values == df2.values

    # get the rows and columns of the different cells
    rows, cols = numpy.where(compare_values == False)

    # save the difference rows and the cell with  difference will have value 'old --> new'
    output_diff = write_only_diferences(df1, df2, rows, cols)

    return False, output_diff


# compare files with multiple sheets
def xlsx_is_equal(xlsx1_path, xlsx2_path, output_path):
    xl = pandas.ExcelFile(xlsx1_path)
    sheet_size = len(xl.sheet_names)

    output = []
    output_sheet_names = []

    # for each sheet will read, compare the dataframes and return the differences dataframe
    for i in range(sheet_size):

        # read file 1 and replace na with 0
        df1 = pandas.read_excel(xlsx1_path, sheet_name=i)
        df1 = df1.fillna(0)

        # read file 2 and replace na with 0
        df2 = pandas.read_excel(xlsx2_path, sheet_name=i)
        df2 = df2.fillna(0)

        # check if is equal and return the differences rows
        equal, diff = sheet_is_equal(df1, df2)

        # if is not iqual append to the arrays of output and sheet names
        if not equal:
            output.append(diff)
            output_sheet_names.append(xl.sheet_names[i])

    # if all sheets are equal return False
    if output == []:
        return False

    # if there is a difference in the sheets, write every difference output in one sheet with the sheet name
    with pandas.ExcelWriter(output_path) as writer:

        for i in range(len(output)):
            output[i].style.applymap(highlight_cells).to_excel(writer, sheet_name=output_sheet_names[i], engine='openpyxl', index=False)

    return True

# names = ['REDA041', 'REDA031', 'REDA022', 'REDA017', 'REDA016', 'REDA014', 'PIBR001', 'PIBR002', 'PAIN014', 'PAIN013', 'PACS008', 'PACS004', 'PACS002', 'HEAD001', 'CAMT060', 'CAMT054', 'CAMT053', 'CAMT052', 'CAMT014', 'ADMI004', 'ADMI002']
#
# # print(xlsx_is_equal('/Users/lucaslaheras/Downloads/teste.xlsx', '/Users/lucaslaheras/Downloads/teste2.xlsx', output_path = 'diferences to .xlsx'))
# for item in names:
#     print(xlsx_is_equal('/Users/lucaslaheras/Downloads/v5.07.1/xlsx/' + item + '.xlsx', '/Users/lucaslaheras/Downloads/v5.06.1/xlsx/' + item + '.xlsx', output_path='diferences ' + item + '.xlsx'))

