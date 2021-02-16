from django.shortcuts import render, get_list_or_404
import requests
import datetime
from django.views.static import serve
# django.contrib.auth.decorators import login_required, user_passes_test
# from templatetags import page_view_tags
import database.views as db
from django.core.paginator import Paginator
import json

from pathlib import Path

# from django.view import generic
# Create your views here.
HOST_SERVER = 'http://127.0.0.1:8000/';

testtoken = 'Token 9378e8bf088a5165f59afcb30bca52af53e0c2ac'
# context = {'Authorization': 'Token f5fbf500f318d33eabd627af173e63e9f538fedb'}
startpage = 1
downloads_path = str(Path.home() / "Downloads")


# @login_required
def modelpage(request):
    context = request.COOKIES['token']
    page_num = request.GET.get('page', startpage)
    page_num = pagecheck(page_num)
    search_term = request.GET.get('search', None)
    search_type = request.GET.get('search_field', None)
    vend = request.GET.get('vendor', None)
    mod_num = request.GET.get('modelnum', None)
    desc = request.GET.get('description', None)
    ord = request.GET.get('ordering', None)

    data = {'page': page_num, 'vendor': vend, 'model_number': mod_num,
            'description': desc, 'ordering': ord, 'search': search_term, 'search_field': search_type}
    header = {'Authorization': context}
    message = requests.get('http://' + request.get_host() + '/models/', headers=header, params=data)
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
    return render(request, 'modelpage.html', {'modlist': modlist, 'page_num': page_num})


# @login_required
def modelpage_all(request):
    context = request.COOKIES['token']
    header = {'Authorization': context}

    message = requests.get('http://' + request.get_host() + '/models/all', headers=header)
    modjson = message.json()

    modlist = []
    for j in modjson:
        model = [j["pk"], j["vendor"], j["model_number"], j["description"], j["comment"], j["calibration_frequency"]]
        modlist.append(model)

    # paginator = Paginator(modlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'model_allpage.html', {'modlist': modlist})


# @login_required
def instrumentpage(request):
    context = request.COOKIES['token']
    page_num = request.GET.get('page', startpage)
    page_num = pagecheck(page_num)
    vend = request.GET.get('vendor', None)
    mod_num = request.GET.get('modelnum', None)
    descr = request.GET.get('description', None)
    serial_num = request.GET.get('serial', None)
    ord = request.GET.get('ordering', None)
    search_term = request.GET.get('search', None)
    search_type = request.GET.get('search_field', None)

    if search_type in ['vendor', 'model_number', 'description']:
        search_type = 'model__' + search_type

    header = {'Authorization': context}

    data = {'page': page_num, 'vendor': vend, 'model_number': mod_num,
            'description': descr, 'serial_number': serial_num, 'ordering': ord,
            'search': search_term, 'search_field': search_type}
    message = requests.get('http://' + request.get_host() + '/instruments/', params=data, headers=header)
    instrjson = message.json()

    results = []
    instrlist = []
    for key, value in instrjson.items():
        if key == 'results':
            results = value
    for j in results:
        temp_model = j["model"]
        instr = [temp_model["vendor"], temp_model["model_number"], j["serial_number"], temp_model["description"],
                 j["most_recent_calibration_date"], j["calibration_expiration_date"],
                 datecheck(j["calibration_expiration_date"])]
        instrlist.append(instr)

    # paginator = Paginator(instrlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'instrumentpage.html',
                  {'instrlist': instrlist, 'page_num': page_num})


# @login_required
def instrumentpage_all(request):
    context = request.COOKIES['token']
    header = {'Authorization': context}

    message = requests.get('http://' + request.get_host() + '/instruments/all', headers=header)
    instrjson = message.json()

    instrlist = []
    for j in instrjson:
        temp_model = j["model"]
        instr = [temp_model["vendor"], temp_model["model_number"], j["serial_number"], temp_model["description"],
                 j["most_recent_calibration_date"], j["calibration_expiration_date"],
                 datecheck(j["calibration_expiration_date"])]
        instrlist.append(instr)

    # paginator = Paginator(instrlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'instrumentpage.html',
                  {'instrlist': instrlist})


# @user_passes_test(lambda u: u.is_superuser)
def import_export(request):
    context = request.COOKIES['token']
    header = {'Authorization': context}
    import_data = []
    if request.method == "GET":
        exp = request.GET.get('export', None)
        if exp != None:
            if exp == '/export-models/':
                data = requests.get('http://' + request.get_host() + exp, headers=header)
                new_file = open(downloads_path+'/mod_export.csv', 'wb').write(data.content)
            if exp == '/export-instruments/':
                data = requests.get('http://' + request.get_host() + exp, headers=header)
                new_file = open(downloads_path+'/instr_export.csv', 'wb').write(data.content)
            if exp == '/export/':
                data = requests.get('http://' + request.get_host() + exp, headers=header)
                new_file = open(downloads_path+'/all_export.zip', 'wb').write(data.content)

    if request.method == "PUT":
        csv_file = request.FILE['file']
        type = request.POST.get('import_type')

        if type == 'models':
            data = requests.post('http://' + request.get_host() + '/import-models', headers=header, file=csv_file)

        else:
            if type == 'instruments':
                data = requests.post('http://' + request.get_host() + '/import-instruments', headers=header, file=csv_file)

    return render(request, 'import_exportpage.html')


def pagecheck(val):
    if int(val) == 0:
        val = 1
    return val


def datecheck(event):
    if event == None:
        return "Noncalibratable"
    else:
        event = datetime.datetime.strptime(event, "%Y-%m-%d").date()
        diff = event - datetime.date.today()
        if event < datetime.date.today():
            return "Expired"
        else:
            if diff.days < 30:
                return "Expiring Soon"
            else:
                return "Calibration Stable"


def get_current_path(request):
    return request.get_full_path()
