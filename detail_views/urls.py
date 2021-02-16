from django.urls import path
from detail_views import views as dv


urlpatterns = [
    path('model-details/<str:pk>', dv.model_detail_page, name='model-details'),
    path('instrument-details/<str:serial>', dv.instrument_detail_page, name='instrument-details'),
    path('pdf/<str:serial>', dv.pdf_gen),
    path('edit-inst/<str:pk><str:serial>', dv.edit_instrument, name='edit-instrument'),
    path('del-inst/<str:pk>', dv.delete_instrument, name='del-inst'),
]
