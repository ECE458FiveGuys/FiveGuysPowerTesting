import json
from datetime import datetime

import requests
from PIL import Image
from django.shortcuts import render, get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# from database import views as db
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Create your views here.
from detail_views.forms import CalibrationForm


def model_detail_page(request, pk=None):
    token = {'Authorization': 'Token 6817972dd66d13c114979cf5be22f93d374e31b2'}

    modeldata = requests.get('http://'+request.get_host()+'/models/', headers=token, params={'pk': pk})
    instrumentsdata = requests.get('http://'+request.get_host()+'/instruments/', headers=token, params={})

    model = modeldata.json()['results'][0]
    instruments = instrumentsdata.json()['results']

    instrumentstopost = []

    for instrument in instruments:
        if str(instrument['model']['pk']) == pk:
            instrumentstopost.append(instrument)

    context = {
        "model": model,
        "instruments": instrumentstopost,
    }

    return render(request, 'model_details.html', context)


def instrument_detail_page(request, serial=None):
    # instrument = get_object_or_404(db.InstrumentViewSet.all(request=request), serial_number=serial)
    token = {'Authorization': 'Token 6817972dd66d13c114979cf5be22f93d374e31b2'}

    instrumentsdata = requests.get('http://'+request.get_host()+'/instruments/', headers=token,
                                   params={'serial_number': serial})

    instrument = instrumentsdata.json()['results'][0]

    calibrationdata = requests.get('http://'+request.get_host()+'/calibration-events/', headers=token,
                                   params={'instrument': instrument['pk']})

    model = instrument['model']
    calibrations = calibrationdata.json()['results']

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
            print(response)


    # If this is a GET (or any other method) create the default form.
    else:
        form = CalibrationForm()
    context = {
        "instrument": instrument,
        "model": model,
        "form": form,
        "user": user,
        "calibrations": calibrations,
    }
    return render(request, 'instrument_details.html', context)


def pdf_gen(request, serial=None):
    token = {'Authorization': 'Token 6817972dd66d13c114979cf5be22f93d374e31b2'}

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    img = Image.open("detail_views/resources/htplogo.png")
    p.drawInlineImage(img, 165, 450)
    # --------------------------------------------------------
    time = datetime.today()
    date = time.strftime("%h-%d-%Y %H:%M:%S")

    instrumentdata = requests.get('http://' + request.get_host() + '/instruments/', headers=token,
                                   params={'serial_number': serial})

    instrument = instrumentdata.json()['results'][0]
    model = instrument['model']

    calibrationdata = requests.get('http://' + request.get_host() + '/calibration-events/', headers=token,
                                   params={'pk': instrument['calibration_history']['pk']})

    calibration = calibrationdata.json()['results'][0]

    p.setLineWidth(.3)
    p.setFont('Helvetica-Bold', 32)
    p.drawString(65, 775, 'CALIBRATION CERTIFICATE')
    p.line(15,700,580,700)

    p.setFont('Helvetica', 15)
    p.drawString(65, 300, 'Model Number: '+model['model_number'])
    p.drawString(65, 275, 'Model Description: '+model['description'])
    p.drawString(65, 250, 'Date of Last Calibration: '+instrument['calibration_history']['date'])
    p.drawString(65, 225, 'Exp. Date: '+instrument['calibration_expiration'])
    p.drawString(65, 200, 'Done by user: '+str(calibration['user']))
    p.drawString(65, 175, 'Comment: '+calibration['comment'])

    p.drawString(65, 150, 'Date of Report: '+date)









    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='calibration_certificate.pdf')
