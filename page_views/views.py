from django.shortcuts import render, get_list_or_404
from database.models import Model
from database.models import Instrument
#from django.view import generic
# Create your views here.
def modelpage(request):
    modlist = get_list_or_404(Model)
    return render(request, 'modelpage.html', {'modlist':modlist})

def instrumentpage(request):
    instrlist = get_list_or_404(Instrument)
    return render(request, 'instrumentpage.html', {'instrlist':instrlist})

