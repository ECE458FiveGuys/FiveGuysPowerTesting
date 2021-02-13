"""FiveGuysPowerTesting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from enum import Enum

from django.contrib import admin

import database
from page_views import views as v
from django.urls import path, include
from detail_views import views as dv
from django.urls import path, include, re_path
from rest_framework import routers, serializers, viewsets
from database import views
from database.views import EquipmentModelViewSet, InstrumentViewSet, CalibrationEventViewSet, VendorAutoCompleteViewSet

router = routers.DefaultRouter()
router.register(r'models', EquipmentModelViewSet)
router.register(r'instruments', InstrumentViewSet)
router.register(r'calibration-events', CalibrationEventViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('models/', include('database.urls')),
    path('model-details/<str:pk>', dv.model_detail_page, name='model-details'),
    path('instrument-details/<str:serial>', dv.instrument_detail_page, name='instrument-details'),
    path('pdf/', dv.pdf_gen),
    path('', include(router.urls)),
    path('', include('database.urls')),
    path('model/', v.modelpage),
    path('instrument/', v.instrumentpage),
    path('', include('user_portal.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
