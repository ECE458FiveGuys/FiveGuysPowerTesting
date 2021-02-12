from django.shortcuts import render, get_list_or_404
import database.views as db
from django.core.paginator import Paginator

# from django.view import generic
# Create your views here.
def modelpage(request):
    modlist = get_list_or_404(db.EquipmentModelViewSet.queryset)
    paginator = Paginator(modlist, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page('page_number')
    return render(request, 'modelpage.html', {'modlist': page_obj})


def instrumentpage(request):
    instrlist = get_list_or_404(db.InstrumentViewSet.queryset)
    paginator = Paginator(instrlist, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page('page_number')
    return render(request, 'instrumentpage.html', {'instrlist': page_obj})
