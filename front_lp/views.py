from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import HttpResponse
import requests
from django.utils.http import is_safe_url
from django.conf import settings



def loginpage(request):
    return render(request, 'loginpage.html')

def tempMainPage(request):
    print('made it here')
    if 'context' in locals():
        print('found the token')
        print(context['Token'])
    else:
        context = {'Token': 'None'}
        print('resetting it')
    return render(request, 'tempMainPage.html', context)


def deleteconfirmation(request):
    print(request.GET)
    text = "hello world"
    context = {'mytext': text}
    return render(request, 'deleteconfirmation.html', context)

# @csrf_exempt
def home(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data1 = {'username':username, 'password':password}
        read1 = requests.post('http://127.0.0.1:8000/auth/token/login/', data=data1)
        response = 'Token ' + str(read1.json().get('auth_token'))
        context = {'Token': response}
        if (len(response)>=20):
            return render(request, 'tempMainPage.html', context)
        else:
            render(request, 'home.html')
    # tokenString = 'Token ' + read1.json().get('auth_token')
    #tokenString = 'Token d7200ac35c77af727d41e0cd06809b2d355b7188'
    #print(tokenString)

    #data2 = {'vendor': 'newguy123', 'model_number': '1238634379', 'description': 'newdesript'}
    #header2 = {'Authorization': tokenString}
    #read2 = requests.get('http://127.0.0.1:8000/models/', headers=header2, data=data2)
    #print(read2.json())
    #print(read2)
    return render(request, 'home.html')



def createmodel(request):
    if request.method =="POST":
        vendor = request.POST.get("vendor")
        model_number = request.POST.get("model_number")
        description = request.POST.get("description")
        comment = request.POST.get("comment")
        calibration_frequency = request.POST.get("calibration_frequency")
        data2 = {'vendor': vendor, 'model_number': model_number, 'description': description,
                 'comment':comment, 'calibration_frequency':calibration_frequency}
        tokenString = 'Token d91b700309be8eaf59a877828e2017d748dcca4b'
        header2 = {'Authorization': tokenString}
        read2 = requests.post('http://127.0.0.1:8000/models/', headers=header2, data=data2)
        context = {'mytext': 'nothing to show yet'}
        if (str(read2.json().get('vendor'))==vendor):
            context = {'intro_phrase': 'Successfully added a model with the following information:',
                       'vendor': 'Vendor Name: ' + vendor,
                       'model_number': 'Model Number: ' + model_number,
                       'description': 'Description: '+ description,
                       'comment': 'Comment: ' + comment,
                       'calibration_frequency': 'Calibration Frequency:' + calibration_frequency}
        return render(request, 'createmodel.html', context)
    else:
        return render(request, 'createmodel.html')

def createinstrument(request):
    if request.method =="POST":
        serial_number = request.POST.get("serial_number")
        model = request.POST.get("model")
        comment = request.POST.get("comment")
        data2 = {'model': model,
                 'serial_number': serial_number,
                 'comment': comment}
        tokenString = 'Token d91b700309be8eaf59a877828e2017d748dcca4b'
        header2 = {'Authorization': tokenString}
        read2 = requests.post('http://127.0.0.1:8000/instruments/', headers=header2, data=data2)
        context = {'mytext': 'nothing to show yet'}
        if (str(read2.json().get('model'))==model):
            context = {'intro_phrase': 'Successfully added an instrument with the following information:',
                       'serial_number': 'Serial Number: ' + serial_number,
                       'model': 'Model: ' + model,
                       'comment': 'Comment: ' + comment}
        return render(request, 'createinstrument.html', context)
    else:
        return render(request, 'createinstrument.html')

def createuser(request):
    if request.method =="POST":

        data2 = {'username': 'hii',
                 'name': 'hello',
                 'email': 'me@duke.com',
                 'password': 'longpassword345',
                 'is_active': 'True'}
        tokenString = 'Token d91b700309be8eaf59a877828e2017d748dcca4b'
        header2 = {'Authorization': tokenString}
        read2 = requests.post('http://127.0.0.1:8000/auth/users/', headers=header2, data=data2)
        print(read2)
        return render(request, 'createuser.html')
        #return render(request, 'createuser.html', context)
    else:
        return render(request, 'createuser.html')