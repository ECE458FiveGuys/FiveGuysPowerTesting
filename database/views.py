from django.shortcuts import render

# Create your views here.
from database import utils
from database.services.model_services.select_models import SelectModels


def get_models(request):
    utils.execute_api(api=SelectModels(
        user_id=request.user_id,
        password=request.password,
        model_id=request.model_id,
        vendor=request.vendor,
        model_number=request.model_number,
        description=request.description,
        calibration_frequency=request.calibration_frequency
    ))