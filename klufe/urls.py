from django.urls import re_path
from klufe import views

urlpatterns = [
    re_path('/on', views.voltageOn),
    re_path('/off', views.voltageOff),
    re_path('/set/AC', views.setACVoltage),
    re_path('/set/DC', views.setDCVoltage),
]
