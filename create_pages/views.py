from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import HttpResponse
import requests
from django.utils.http import is_safe_url
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from create_pages.models import City


def showlist(request):
    data2 = {'vendor': ''}
    header2 = {'Authorization': request.COOKIES['token']}
    print(header2)
    read2 = requests.get('http://' + request.get_host() + '/vendors/', headers=header2, data=data2)
    results = read2.json
    print(results)
    return render(request, "home.html", {"showcity": results})

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data1 = {'username':username, 'password':password}
        read1 = requests.post('http://'+request.get_host()+'/auth/token/login/', data=data1)
        tokenString = 'Token ' + str(read1.json().get('auth_token'))
        if (len(tokenString)>=20):
            response = render(request, 'intermediatepage.html')
            response.set_cookie('token', tokenString)
            return response
        else:
            print(read1.json())
            context = {'response': read1.json()}
            return render(request, 'login.html', context)
    return render(request, 'login.html')

def intermediatepage(request):
    return render(request, 'intermediatepage.html')

def createmodel(request):
    data2 = {'vendor': ''}
    header2 = {'Authorization': request.COOKIES['token']}
    print(header2)
    read2 = requests.get('http://' + request.get_host() + '/vendors/', headers=header2, data=data2)
    results = read2.json
    print(results)
    context = {"showcity": results}
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
    if request.method =="POST":
        model = request.POST.get("model")
        serial_number = request.POST.get("serial_number")
        comment = request.POST.get("comment")
        data2 = {'model': model,
                 'serial_number': serial_number,
                 'comment': comment}
        header2 = {'Authorization': token}
        read2 = requests.post('http://' + request.get_host() + '/instruments/', headers=header2, data=data2)
        context = {}
        if (str(read2.json().get('model'))==model):
            context = {'intro_phrase': 'Successfully added an instrument with the following information:',
                       'serial_number': 'Serial Number: ' + serial_number,
                       'model': 'Model: ' + model,
                       'comment': 'Comment: ' + comment}
        else:
            context = {'intro_phrase': read2.json()}
        return render(request, 'createinstrument.html', context)
    else:
        return render(request, 'createinstrument.html')

def createuser(request):
    if request.method =="POST":
        username = request.POST.get("username")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        data2 = {'username': username,
                 'name': name,
                 'email': email,
                 'password': password,
                 'is_active': 'True'}
        header2 = {'Authorization': token}
        read2 = requests.post('http://'+request.get_host()+'/auth/users/', headers=header2, data=data2)
        context = {}
        if (str(read2.json().get('username')) == username):
            context = {'intro_phrase': 'Successfully added a user with the following information:',
                       'username': 'Username: ' + username,
                       'name': 'Name: ' + name,
                       'email': 'Email : ' + email}
        else:
            context = {'intro_phrase': read2.json()}
        return render(request, 'createuser.html', context)
    else:
        return render(request, 'createuser.html')