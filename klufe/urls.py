from django.urls import re_path
from klufe import views

urlpatterns = [
    re_path('', views.setDC),
]
