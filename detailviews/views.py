from django.shortcuts import render
from database import views as db

# Create your views here.
def detailspage(request):
    context = {
        "model": db.EquipmentModelViewSet.queryset.first(),
        "instruments": db.InstrumentViewSet.queryset
    }
    return render(request, 'modeldetails.html', context)
