from django.shortcuts import render, get_list_or_404
import requests
import database.views as db
from django.core.paginator import Paginator
import json
from types import SimpleNamespace

# from django.view import generic
# Create your views here.
token = 'f5fbf500f318d33eabd627af173e63e9f538fedb'
context = {'Token': token}
startpage = 1

def modelpage(request):
    page_num = request.GET.get('page', startpage)
    vend = request.GET.get('vendor', None)
    mod_num = request.GET.get('modelnum', None)
    desc = request.GET.get('description', None)
    ord = request.GET.get('ordering', None)

    data = {'Authorization': token, 'page': page_num, 'vendor': vend,
            'model_number': mod_num, 'description': desc, 'ordering': ord}
    modjson = requests.get('http://127.0.0.1:8000/models/', data)

    modlist = []
    for j in modjson:
        model = json.loads(j, object_hook=lambda d: SimpleNamespace(**d))
        modlist.append(model)

    # paginator = Paginator(modlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'modelpage.html', {'modlist': modlist, 'page_num': page_num})


def instrumentpage(request, page=1, vendor='',modelnum='', description='',serial='', ordering=''):
    page_num = request.GET.get('page', page)
    vend = request.GET.get('vendor', vendor)
    mod_num = request.GET.get('modelnum', modelnum)
    descr = request.GET.get('description', description)
    serial_num = request.GET.get('serial', serial)
    ord = request.GET.get('ordering', ordering)

    data = {'Authorization': token, 'page': page_num, 'vendor': vend,
            'model_number': mod_num, 'description': descr,
            'serial_number': serial_num, 'ordering': ord}
    instrjson = requests.get('http://127.0.0.1:8000/models/', data)

    instrlist = []
    for j in instrjson:
        instr = json.loads(j, object_hook=lambda d: SimpleNamespace(**d))
        instrlist.append(instr)

    # paginator = Paginator(instrlist, 25)
    # page_obj = paginator.get_page(page_number)
    return render(request, 'instrumentpage.html', {'instrlist': instrlist, 'page_num': page_num})

def import_export(request):
    return render(request)
