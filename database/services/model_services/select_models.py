from database.models import Model


class SelectModels:

    def execute(self):
        return Model.objects
