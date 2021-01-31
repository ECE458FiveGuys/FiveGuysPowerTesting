from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.exceptions import IllegalAccessException, NoSuchEntryExistsException
from database.models import Model
from database.services.service import Service


class DeleteModel(Service):

    def __init__(
            self,
            user,
            model_id
    ):
        self.user = user
        self.model_id = model_id

    def execute(self):
        if not self.user.admin:
            raise IllegalAccessException()
        try:
            Model.objects.get(id=self.model_id).delete()
        except ObjectDoesNotExist:
            raise NoSuchEntryExistsException()
