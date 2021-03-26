from django.urls import re_path
from klufe import views

urlpatterns = [
    re_path('/on', views.voltage_onn),
    re_path('/off', views.voltage_off),
    re_path('/set/AC', views.set_ACVoltage),
    re_path('/set/DC', views.set_DCVoltage),
]
