from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import HttpResponse
import requests
from django.utils.http import is_safe_url
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from create_pages.models import City
from django.urls import reverse
import django.core.exceptions

global vendorName
global modelNumber

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data1 = {'username':username, 'password':password}
        read1 = requests.post('http://'+request.get_host()+'/auth/token/login/', data=data1)
        tokenString = 'Token ' + str(read1.json().get('auth_token'))
        if (len(tokenString)>=20):
            context = {'response': 'Successful Logged in. Click button to proceed'}
            response = render(request, 'modelpage.html')
            response.set_cookie('token', tokenString)
            return render(request, 'login.html', context)
        else:
            print(read1.json())
            context = {'response': read1.json()}
            return render(request, 'login.html', context)
    return render(request, 'login.html')

def pickvendor(request):
    try:
        header2 = {'Authorization': request.COOKIES['token']}
    except KeyError:
        context = {'response': 'Please login before continuing'}
        return render(request, 'login.html', context)
    data2 = {'vendor': ''}
    read2 = requests.get('http://' + request.get_host() + '/vendors/', headers=header2, data=data2)
    results = read2.json
    context = {"availableVendors": results}
    if request.method == "POST":
        vendor = request.POST.get("vendor")
        global vendorName
        vendorName = vendor
        print(vendorName)
        response = render(request, 'pickmodelnumber.html')
        response.set_cookie('vendor', vendor)
    return render(request, 'pickvendor.html')

def pickmodelnumber(request):
    try:
        header2 = {'Authorization': request.COOKIES['token']}
    except KeyError:
        context = {'response': 'Please login before continuing'}
        return render(request, 'login.html', context)
    try:
        vendorName = request.COOKIES['vendor']
    except KeyError:
        context = {'response': 'Please enter vendor before continuing'}
        return render(request, 'pickmodelnumber.html', context)
    print(vendorName)
    read2 = requests.get('http://' + request.get_host() + '/model_numbers/?vendor='+vendorName, headers=header2)
    results = read2.json
    context = {"availableModelNumbers": results}
    if request.method == "POST":
        model_number = request.POST.get("model_number")
        global modelNumber
        modelNumber = model_number
        print(modelNumber)
        response = render(request, 'createinstrument.html')
        response.set_cookie('model_number', model_number)
    return render(request, 'pickmodelnumber.html')

def createmodel(request):
    try:
        header2 = {'Authorization': request.COOKIES['token']}
    except KeyError:
        context = {'response': 'Please login before continuing'}
        return render(request, 'login.html', context)
    data2 = {'vendor': ''}
    print(header2)
    read2 = requests.get('http://' + request.get_host() + '/vendors/', headers=header2, data=data2)
    results = read2.json
    context = {"availableVendors": results}
    if request.method =="POST":
        vendor = request.POST.get("vendor")
        model_number = request.POST.get("model_number")
        description = request.POST.get("description")
        comment = request.POST.get("comment")
        calibration_frequency = request.POST.get("calibration_frequency")
        data2 = {'vendor': vendor, 'model_number': model_number, 'description': description,
                 'comment':comment, 'calibration_frequency':calibration_frequency}
        header2 = {'Authorization': request.COOKIES['token']}
        print(header2)
        read2 = requests.post('http://'+request.get_host()+'/models/', headers=header2, data=data2)
        if (str(read2.json().get('vendor'))==vendor):
            context = {'intro_phrase': 'Successfully added a model with the following information:',
                       'vendor': 'Vendor Name: ' + vendor,
                       'model_number': 'Model Number: ' + model_number,
                       'description': 'Description: '+ description,
                       'comment': 'Comment: ' + comment,
                       'calibration_frequency': 'Calibration Frequency: ' + calibration_frequency}
        else:
            context = {'intro_phrase': read2.json()}
        return render(request, 'createmodel.html', context)
    else:
        return render(request, 'createmodel.html', context)

def createinstrument(request):
    try:
        header2 = {'Authorization': request.COOKIES['token']}
    except KeyError:
        context = {'response': 'Please login before continuing'}
        return render(request, 'login.html', context)
    global vendorName
    read2 = requests.get('http://' + request.get_host() + '/model_numbers/?vendor=' + vendorName, headers=header2)
    results = read2.json
    ks = list(results)
    modelNumber = ks[0]
    context = {'vendor':vendorName, 'model_number':modelNumber}
    #now need to find the pk that goes into the model input
    read2 = requests.post('http://' + request.get_host() + '/models/?vendor=' + vendorName + '&model_number=' + modelNumber, headers=header2)
    print(read2.json)
    if request.method =="POST":
        serial_number = request.POST.get("serial_number")
        comment = request.POST.get("comment")
        data2 = {'model': model,
                 'serial_number': serial_number,
                 'comment': comment}
        read2 = requests.post('http://' + request.get_host() + '/instruments/', headers=header2, data=data2)
        if (str(read2.json().get('model'))==model):
            context = {'intro_phrase': 'Successfully added an instrument with the following information:',
                       'serial_number': 'Serial Number: ' + serial_number,
                       'model': 'Model: ' + model,
                       'comment': 'Comment: ' + comment}
        else:
            context = {'intro_phrase': read2.json()}
        return render(request, 'oldcreateinstrument.html', context)
    else:
        return render(request, 'oldcreateinstrument.html')

def createuser(request):
    try:
        headerContainingToken = {'Authorization': request.COOKIES['token']}
    except KeyError:
        context = {'response': 'Please login before continuing'}
        return render(request, 'login.html', context)

    if request.method =="POST":
        informationNeeded = ['username', 'name', 'email', 'password']
        dataGivenInPost = createData(informationNeeded, request)
        read2 = requests.post('http://'+request.get_host()+'/auth/users/', headers=headerContainingToken, data=dataGivenInPost)

        if read2.ok:
            informationNeededToBeDisplayed = ['username', 'name', 'email']
            context = generateSuccessMessageContext(informationNeededToBeDisplayed, read2)
        else:
            context = {'message1': read2.json()}

        return render(request, 'createuser.html', context)
    else:
        return render(request, 'createuser.html')

def createData(informationNeeded, request):
    returnData = {}
    for i in range(len(informationNeeded)):
        key = informationNeeded[i]
        info = request.POST.get(key)
        returnData[key] = info
    return returnData

def generateSuccessMessageContext(informationNeeded, read2):
    context = {'message1': 'Successfully added the following to the database:'}
    for i in range(len(informationNeeded)):
        field = informationNeeded[i] + ": "
        valueAdded = read2.json()[informationNeeded[i]]
        toBeDisplayed = field + valueAdded
        key = 'message' + str(i+2)
        context[key] = toBeDisplayed
    return context