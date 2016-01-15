import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1

filename = sys.argv[1]
fp = open(filename, 'rb')

parser = PDFParser(fp)
doc = PDFDocument(parser)
doc.initialize()    
fields = resolve1(doc.catalog['AcroForm'])['Fields']
for i in fields:
    field = resolve1(i)
    name, value = field.get('T'), field.get('V')
    print('{0}: {1}'.format(name, value))