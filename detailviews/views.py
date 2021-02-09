from django.shortcuts import render

# Create your views here.
def detailspage(request):
    return render(request, 'detailpopup.html')