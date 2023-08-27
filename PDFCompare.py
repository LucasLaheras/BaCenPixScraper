import PyPDF2
import os


def pdf2text(pdf_path, return_pages=False):
    text = ""

    # opening method will be rb
    pdffileobj = open(pdf_path, 'rb')

    # create reader variable that will read the pdffileobj
    pdfreader = PyPDF2.PdfFileReader(pdffileobj, strict=False)

    # This will store the number of pages of this pdf file
    size = pdfreader.numPages

    for j in range(size):
        # variable that will select the selected pages
        pageobj = pdfreader.getPage(j)

        # this text variable will store all text data from pdf file
        text = text + pageobj.extractText()

    pdffileobj = 0
    pdfreader = 0

    if return_pages:
        return text, size

    return text


def pdf_is_equal(pdf1_path, pdf2_path):
    pdf1_text, pdf1_size = pdf2text(pdf1_path, True)
    pdf2_text, pdf2_size = pdf2text(pdf2_path, True)

    if pdf1_size == pdf2_size and pdf1_text == pdf2_text:
        return True

    return False
