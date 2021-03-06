#!/usr/bin/python3

import os

import PyPDF2
from datetime import date
import datetime

import pathlib

template_path = str(pathlib.Path(__file__).parent.absolute()) + "/empty.pdf"

#Edit fields with correct data
import_dict = {
"Geboortedatum": "2020-01-01",
"Voorletter(s) en achternaam":"Henk Acker" ,
"Adres": "Radioweg 1" ,
"Woonplaats": "Amsterdam",
"Plaats ondertekening": "Amsterdam" ,
#optional:
"Toelichting medische hulp voor mijzelf": "",
"Toelichting medische hulp voor iemand anders":"",
# Keep fixed
"Ik verklaar dat ik dit formulier naar waarheid heb ingevuld 2":"/Akkoord" ,
"verklaar hierbij dat ik van (datum)": str(date.today()) ,
"tot en met (datum)": str(date.today()+ datetime.timedelta(days=1)) ,
"Datum ondertekening": str(date.today()),
}

select_one = {
"Ik moet werken en heb de Werkgeversverklaring Avondklok bij me" ,
"Ik heb dringend medische hulp nodig (of een dier) " ,
"Iemand anders heeft dringend mijn hulp nodig" ,
"Ik reis naar het buitenland, en kan dat aantonen" ,
"Ik ben onderweg van of naar een uitvaart en kan dit aantonen",
"Ik ben onderweg in verband met een oproep van justitie" ,
"Ik ben onderweg van of naar een live-programma en kan dit aantonen" ,
"Ik ben onderweg van of naar een examen of tentamen" ,
}

# Select one of the options from the select_one
option = {
"Ik moet werken en heb de Werkgeversverklaring Avondklok bij me" ,
}

# Based on with https://stackoverflow.com/questions/35538851/how-to-check-uncheck-checkboxes-in-a-pdf-with-python-preferably-pypdf2
# with some modifications
def updateCheckboxValues(page, fields):
    for j in range(0, len(page['/Annots'])):
        writer_annot = page['/Annots'][j].getObject()
        if writer_annot.get("/Parent") and writer_annot.get("/Parent").getObject().get("/T") in fields:
           writer_annot.update({
                    PyPDF2.generic.NameObject("/AS"):PyPDF2.generic.NameObject("/0"),
           })
           # For some reason the /V object needs to be put in the parent
           writer_annot.get("/Parent").getObject().update({
                    PyPDF2.generic.NameObject("/V"):PyPDF2.generic.NameObject("/0")
           })

def fixEvice(page):
    for j in range(0, len(page['/Annots'])):
        writer_annot = page['/Annots'][j].getObject()
        if not writer_annot.get("/AS") and writer_annot.get("/AP"):
            del writer_annot["/AP"]
        if "waarheid" in str(writer_annot.get("/T")):
           writer_annot.update({
                    PyPDF2.generic.NameObject("/AS"):PyPDF2.generic.NameObject("/Akkoord"),
           })

# https://stackoverflow.com/questions/58898542/update-a-fillable-pdf-using-pypdf2
def set_need_appearances_writer(writer):
    # See 12.7.2 and 7.7.2 for more information: http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
    try:
        catalog = writer._root_object
        # get the AcroForm tree
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                PyPDF2.generic.NameObject("/AcroForm"): PyPDF2.generic.IndirectObject(len(writer._objects), 0, writer)
            })

        need_appearances = PyPDF2.generic.NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = PyPDF2.generic.BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer

template = PyPDF2.PdfFileReader(template_path)

writer = PyPDF2.PdfFileWriter()

first_page = template.getPage(0)
writer.updatePageFormFieldValues(first_page, fields=import_dict)
fixEvice(first_page)
writer.addPage(first_page)
first_page = template.getPage(1)
writer.addPage(first_page)
writer.updatePageFormFieldValues(writer.getPage(1), fields=import_dict)
updateCheckboxValues(writer.getPage(1),option)
set_need_appearances_writer(writer)
fixEvice(first_page)
with open("output.pdf","wb") as new:
    writer.write(new)


