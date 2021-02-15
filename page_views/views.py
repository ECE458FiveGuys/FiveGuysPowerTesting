from django.shortcuts import render, get_list_or_404
import requests
from datetime import date
#from templatetags import page_view_tags
import database.views as db
from django.core.paginator import Paginator
import json

# from django.view import generic
# Create your views here.
token = 'Token f5fbf500f318d33eabd627af173e63e9f538fedb'
context = {'Authorization': 'Token f5fbf500f318d33eabd627af173e63e9f538fedb'}
startpage = 1


def modelpage(request):
    page_num = request.GET.get('page', startpage)
    page_num = pagecheck(page_num)
    vend = request.GET.get('vendor', None)
    mod_num = request.GET.get('modelnum', None)
    desc = request.GET.get('description', None)
    ord = request.GET.get('ordering', None)

    data = {'page': page_num, 'vendor': vend,
            'model_number': mod_num, 'description': desc, 'ordering': ord}
    header = context
    message = requests.get('http://127.0.0.1:8000/models/', headers=header, data=data)
    modjson = message.json()

    results = []
    modlist = []
    for key, value in modjson.items():
        if key == 'results':
            results = value
    for j in results:
        model = [j["pk"], j["vendor"], j["model_number"], j["description"], j["comment"], j["calibration_frequency"]]
        modlist.append(model)

    # paginator = Paginator(modlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'modelpage.html', {'modlist': modlist,
                                              'page_num': page_num, 'c_path': get_current_path(request)})


def instrumentpage(request):
    page_num = request.GET.get('page', startpage)
    page_num = pagecheck(page_num)
    vend = request.GET.get('vendor', '')
    mod_num = request.GET.get('modelnum', '')
    descr = request.GET.get('description', '')
    serial_num = request.GET.get('serial', '')
    ord = request.GET.get('ordering', '')

    data = {'page': page_num, 'vendor': vend,
            'model_number': mod_num, 'description': descr,
            'serial_number': serial_num, 'ordering': ord}
    message = requests.get('http://127.0.0.1:8000/models/', data=data, headers=context)
    instrjson = message.json()

    results = []
    instrlist = []
    for key, value in instrjson.items():
        if key == 'results':
            results = value
    for j in results:
        temp_model = j["model"]
        instr = [temp_model["vendor"], temp_model["model_number"], j["serial_number"], temp_model["description"],
                 j["calibration_history"], j["calibration_expiration_date"],
                 datecheck(j["calibration_expiration_date"])]
        instrlist.append(instr)

    # paginator = Paginator(instrlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'instrumentpage.html',
                  {'instrlist': instrlist, 'page_num': page_num, 'c_path': get_current_path(request)})


def import_export(request):
    return render(request)


def pagecheck(val):
    if int(val) == 0:
        val = 1
    return val


def datecheck(event):
    if event == '':
        return "Noncalibratable"
    else:
        event = datetime.datetime.strptime(event, "%Y-%m-%d").date()
        diff = event - date.today()
        if event < date.today():
            return "Expired"
        else:
            if diff.days < 30:
                return "Expiring Soon"
            else:
                return "Calibration Stable"


def get_current_path(request):
    return request.get_full_path()
