from django.shortcuts import render
from database import views as db

# Create your views here.
def detailspage(request):
    fields = db.
    return render(request, 'modeldetails.html')