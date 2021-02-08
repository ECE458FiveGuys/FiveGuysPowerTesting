from django.shortcuts import render

# Create your views here.
def modelpage(request):
    return render(request, 'modelpage.html')

def instrumentpage(request):
    return render(request, 'instrumentpage.html')
