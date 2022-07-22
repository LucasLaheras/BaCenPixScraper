import PyPDF2


def pdf2text(pdf_path, return_pages=False):
    # opening method will be rb
    pdffileobj = open(pdf_path, 'rb')

    # create reader variable that will read the pdffileobj
    pdfreader = PyPDF2.PdfFileReader(pdffileobj)

    # This will store the number of pages of this pdf file
    x = pdfreader.numPages

    # create a variable that will select the selected number of pages
    pageobj = pdfreader.getPage(x-1)

    # create text variable which will store all text datafrom pdf file
    text = pageobj.extractText()

    if return_pages:
        return text, return_pages

    return text


def pdf_is_equal(pdf1_path, pdf2_path):
    pdf1_text, pdf1_size = pdf2text(pdf1_path, True)
    pdf2_text, pdf2_size = pdf2text(pdf2_path, True)

    if pdf1_size == pdf2_size and pdf1_text == pdf2_text:
        return True

    return False
