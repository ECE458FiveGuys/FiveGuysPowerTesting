from django.db import models

from django.core.validators import RegexValidator

from database.constants import CATEGORY_LENGTH


class InstrumentCategory(models.Model):
    name = models.CharField(blank=False, unique=True, max_length=CATEGORY_LENGTH,
                            validators=[RegexValidator("^[\S]*$",
                                                       message="Name of a category can only contain alphanumeric "
                                                               "characters and underscores.")])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
