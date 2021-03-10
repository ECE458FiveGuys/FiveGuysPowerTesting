from django.urls import include, path
from rest_framework import routers

from database import views
from database.views import *

router = routers.DefaultRouter()
router.register(r'models', ModelViewSet)
router.register(r'instruments', InstrumentViewSet, basename='Instrument')
router.register(r'calibration-events', CalibrationEventViewSet)
router.register(r'model-categories', ModelCategoryViewSet)
router.register(r'instrument-categories', InstrumentCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('export/', views.export),
    path('import-models/', ModelUploadView.as_view()),
    path('import-instruments/', InstrumentUploadView.as_view())
]
