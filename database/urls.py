from django.urls import re_path, path

from database import views
from database.views import VendorAutoCompleteViewSet

urlpatterns = [
    path('export-instruments/', views.export_instruments),
    path('export-models/', views.export_models),
    path('export/', views.export),
    path('import-models/', views.import_models),
    path('import-instruments/', views.import_instruments),
    re_path(r'^vendors(?P<vendor>.+)', VendorAutoCompleteViewSet.as_view())
]