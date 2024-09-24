import PyPDF2
import os
import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfquery import PDFQuery

def compare_pdfs(file1, file2):
    """
    Compare two PDF files and return True if they are identical, False otherwise.
    """
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            # Create PDFDocument objects
            parser1 = PDFParser(f1)
            parser2 = PDFParser(f2)
            doc1 = PDFDocument(parser1)
            doc2 = PDFDocument(parser2)

            # Create PDFResourceManager objects
            rsrcmgr1 = PDFResourceManager()
            rsrcmgr2 = PDFResourceManager()

            # Create PDFPageInterpreter objects
            laparams = LAParams()
            device1 = PDFPageAggregator(rsrcmgr1, laparams=laparams)
            device2 = PDFPageAggregator(rsrcmgr2, laparams=laparams)
            interpreter1 = PDFPageInterpreter(rsrcmgr1, device1)
            interpreter2 = PDFPageInterpreter(rsrcmgr2, device2)

            # Process the PDF pages
            for page1, page2 in zip(PDFPage.create_pages(doc1), PDFPage.create_pages(doc2)):
                interpreter1.process_page(page1)
                interpreter2.process_page(page2)

                # Extract the text from the pages
                layout1 = device1.get_result()
                layout2 = device2.get_result()
                text1 = ''
                text2 = ''
                for element in layout1:
                    if isinstance(element, pdfminer.layout.LTTextContainer):
                        text1 += element.get_text()
                for element in layout2:
                    if isinstance(element, pdfminer.layout.LTTextContainer):
                        text2 += element.get_text()

                text1 = {*text1}
                text2 = {*text2}
                diff_text = text1 - text2

                # Compare the text with 10 character margin
                if len(diff_text) > 10:
                    return False
    except:
        print("ERROR COMPARISON " + file1)
    return True


def pdf2text(pdf_path, return_pages=False):
    text = ""

    # opening method will be rb
    pdffileobj = open(pdf_path, 'rb')
    # print( 'lendo '+ pdf_path)
    # create reader variable that will read the pdffileobj
    pdfreader = PyPDF2.PdfFileReader(pdffileobj, strict=False)

    # This will store the number of pages of this pdf file
    size = pdfreader.numPages

    for j in range(int((3/4)*size)):
        # variable that will select the selected pages
        pageobj = pdfreader.getPage(j)

        # this text variable will store all text data from pdf file
        text = text + pageobj.extractText()
    pdffileobj.close()

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
