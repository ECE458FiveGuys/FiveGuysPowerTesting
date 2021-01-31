from database.models import Model
from database.services.service import Service


class SelectModels(Service):

    def execute(self):
        return Model.objects.all()
