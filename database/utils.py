from django.core import serializers
from django.http import HttpResponse

from database.exceptions import UserError


def execute_api(API):
    try:
        return HttpResponse(serializers.serialize("json", API.execute()))
    except UserError as e:
        return HttpResponse(e.message)
