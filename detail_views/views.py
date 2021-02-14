from datetime import datetime

import requests
from PIL import Image
from django.shortcuts import render, get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from database import views as db
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Create your views here.
from detail_views.forms import CalibrationForm


def model_detail_page(request, pk=None):
    model = get_object_or_404(db.EquipmentModelViewSet.queryset, pk=pk)
    context = {
        "model": model,
        "instruments": db.InstrumentViewSet.queryset.all().filter(model=model),
    }

    return render(request, 'model_details.html', context)


def instrument_detail_page(request, serial=None):
    instrument = get_object_or_404(db.InstrumentViewSet.queryset.all(), serial_number=serial)
    token = {'Authorization': 'Token 6817972dd66d13c114979cf5be22f93d374e31b2'}
    user = request.user.id

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = CalibrationForm(request.POST)

        if not form.is_valid():
            print("form isn't valid")

            # redirect to a new URL:
            #TODO form submission response
        else:
            print("form is valid")
            formdict = form.data.dict()
            response = requests.post('http://'+request.get_host()+'/calibration-events/', headers=token, data=formdict)


    # If this is a GET (or any other method) create the default form.
    else:
        form = CalibrationForm()

    context = {
        "instrument": instrument,
        "model": instrument.model,
        "instruments": db.InstrumentViewSet.queryset.all(),
        "form": form,
        "user": user,
    }
    return render(request, 'instrument_details.html', context)


def pdf_gen(request, serial=None):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # p.drawString(100, 100, "Instrument Calibration Certificate")
    img = Image.open("detail_views/resources/htplogo.png")
    # img = img.rotate(90)
    p.drawInlineImage(img, 165, 450)

    # style_sheet = getSampleStyleSheet()

    # --------------------------------------------------------
    # time = datetime.today()
    # date = time.strftime("%h-%d-%Y %H:%M:%S")
    # c = canvas.Canvas(self.__pdfName)
    # p.setPageSize((16 * inch, 22 * inch))
    # textobj = p.beginText()
    # textobj.setTextOrigin(inch, 20 * inch)
    # textobj.textLines('''
    #             This is the scanning report of %s.
    #             ''' , style_sheet['Heading1'])
    # textobj.textLines('''
    #             Date: %s
    #             ''' % date)
    # # for line in self.__text:
    # #     textobj.textLine(line.strip())
    # p.drawText(textobj)
    # p.h1('Test')

    # --------------------------------------------------------

    instrument = get_object_or_404(db.InstrumentViewSet.queryset.all(), serial_number=serial)
    model = instrument.model
    token = {'Authorization': 'Token 6817972dd66d13c114979cf5be22f93d374e31b2'}
    print(instrument.calibration_history)
    p.setLineWidth(.3)
    p.setFont('Helvetica-Bold', 32)
    p.drawString(65, 775, 'CALIBRATION CERTIFICATE')
    p.line(15,700,580,700)

    p.setFont('Helvetica', 15)
    p.drawString(65, 300, 'Model Number: '+model.model_number)
    p.drawString(65, 275, 'Model Description: '+model.description)
    p.drawString(65, 250, 'Date of Last Calibration: '+instrument.calibration_history[0].date)
    p.drawString(65, 225, 'Exp. Date: '+'')
    p.drawString(65, 200, 'Done by user: '+instrument.calibration_history[0].user)
    p.drawString(65, 175, 'Comment: '+instrument.calibration_history[0].comment)

    p.drawString(65, 150, 'Date of Report: '+date)








    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='calibration_certificate.pdf')
