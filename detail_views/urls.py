from django.urls import path, re_path
from detail_views import views as dv


urlpatterns = [
    path('model-details/<str:pk>/', dv.model_detail_page, name='model-details'),
    path('instrument-details/<str:serial>', dv.instrument_detail_page, name='instrument-details'),
    path('pdf/<str:pk>', dv.pdf_gen),
    path('edit-inst/<str:serial><str:pk>/', dv.edit_instrument, name='edit-instrument'),
    path('del-inst/<str:pk>/', dv.delete_instrument, name='del-inst'),
    path('edit-mod/<str:pk>/', dv.edit_model, name='edit-model'),
    path('del-mod/<str:pk>/', dv.delete_model, name='del-model'),
    path('no-calibrations/<str:serial>/', dv.calibration_message),
]
