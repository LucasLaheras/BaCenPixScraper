import os

def txt_is_equal(txt1, txt2):
    # read file1
    file = open(txt1)
    data1 = file.read()
    file.close()

    # read file12
    file = open(txt2)
    data2 = file.read()
    file.close()

    if data1 == data2:
        return True

    return False
