from datetime import datetime

import requests
from django.shortcuts import redirect

from PIL import Image
from django.shortcuts import render

# from database import views as db
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Create your views here.
from detail_views.forms import *

#token = {'Authorization': 'Token eadb51c79b15f8eb55d49e0a9228beea6b468c64'}


def model_detail_page(request, pk=None):
    header2 = {'Authorization': request.COOKIES['token']}

    modeldata = requests.get('http://' + request.get_host() + '/models/', headers=header2, params={'pk': pk})
    instrumentsdata = requests.get('http://' + request.get_host() + '/instruments/', headers=header2, params={})

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
    header2 = {'Authorization': request.COOKIES['token']}

    instrumentsdata = requests.get('http://' + request.get_host() + '/instruments/', headers=header2,
                                   params={'serial_number': serial})

    instrument = instrumentsdata.json()['results'][0]

    calibrationdata = requests.get('http://' + request.get_host() + '/calibration-events/', headers=header2,
                                   params={'instrument': instrument['pk']})

    model = instrument['model']
    calibrations = calibrationdata.json()['results']

    user_data = requests.get('http://' + request.get_host() + '/auth/users/me/', headers=header2)
    user = user_data.json()['id']

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = CalibrationForm(request.POST)

        if not form.is_valid():
            print("form isn't valid")

        # redirect to a new URL:
        # TODO form submission response
        else:
            print("form is valid")
            formdict = form.data.dict()
            response = requests.post('http://' + request.get_host() + '/calibration-events/', headers=header2,
                                     data=formdict)
            print(formdict)


    # If this is a GET (or any other method) create the default form.
    cal_form = CalibrationForm()
    edit_form = InstrumentsEditForm()

    context = {
        "instrument": instrument,
        "model": model,
        "cal_form": cal_form,
        "edit_form": edit_form,
        "user": user,
        "calibrations": calibrations,
    }
    return render(request, 'instrument_details.html', context)


def edit_instrument(request, pk=None, serial=None):
    header2 = {'Authorization': request.COOKIES['token']}
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = InstrumentsEditForm(request.POST)
        if not form.is_valid():
            print("form isn't valid")

        # redirect to a new URL:
        #TODO form submission response
        else:
            print("form is valid")
            formdict = form.data.dict()
            response = requests.put('http://' + request.get_host() + '/instruments/'+pk+'/', headers=header2, data=formdict)
            print(response)
            print(formdict)

    ret = redirect('/instrument-details/'+serial)#TODO
    return ret

def delete_instrument(request, pk=None):
    header2 = {'Authorization': request.COOKIES['token']}

    # Create a form instance and populate it with data from the request (binding):

    # redirect to a new URL:
    #TODO form submission response
    print("form is valid")
    response = requests.delete('http://' + request.get_host() + '/instruments/'+pk+'/', headers=header2)
    print(response)

    ret = redirect('/instrument/')#TODO
    return ret


def pdf_gen(request, serial=None):
    header2 = {'Authorization': request.COOKIES['token']}
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    img = Image.open("detail_views/resources/htplogo.png")
    p.drawInlineImage(img, 165, 450)
    # --------------------------------------------------------
    time = datetime.today()
    date = time.strftime("%h-%d-%Y %H:%M:%S")

    instrumentdata = requests.get('http://' + request.get_host() + '/instruments/', headers=header2,
                                  params={'serial_number': serial})

    instrument = instrumentdata.json()['results'][0]
    model = instrument['model']

    calibrationdata = requests.get('http://' + request.get_host() + '/calibration-events/', headers=header2,
                                   params={'pk': instrument['calibration_history']['pk']})

    calibration = calibrationdata.json()['results'][0]

    p.setLineWidth(.3)
    p.setFont('Helvetica-Bold', 32)
    p.drawString(65, 775, 'CALIBRATION CERTIFICATE')
    p.line(15, 700, 580, 700)

    p.setFont('Helvetica', 15)
    p.drawString(65, 300, 'Model Number: ' + model['model_number'])
    p.drawString(65, 275, 'Model Description: ' + model['description'])
    p.drawString(65, 250, 'Date of Last Calibration: ' + instrument['calibration_history']['date'])
    p.drawString(65, 225, 'Exp. Date: ' + instrument['calibration_expiration'])
    p.drawString(65, 200, 'Done by user: ' + str(calibration['user']))
    p.drawString(65, 175, 'Comment: ' + calibration['comment'])

    p.drawString(65, 150, 'Date of Report: ' + date)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='calibration_certificate.pdf')
