from django.urls import include, path, re_path
from rest_framework import routers

from database import views
from database.views import *

router = routers.DefaultRouter()
router.register(r'models', EquipmentModelViewSet)
router.register(r'instruments', InstrumentViewSet, basename='Instrument')
router.register(r'calibration-events', CalibrationEventViewSet)
router.register(r'model-categories', ModelCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('export-instruments/', views.export_instruments),
    path('export-models/', views.export_models),
    path('export/', views.export),
    path('import-models/', views.import_models),
    path('import-instruments/', views.import_instruments),
    re_path(r'^vendors/', VendorAutoCompleteViewSet.as_view()),
    re_path(r'^model_numbers/', ModelAutocompleteViewSet.as_view())
]
