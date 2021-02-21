from datetime import timedelta

from django.test import TestCase

from database.models.model import Model
from database.models.model_category import ModelCategory


class CreateModelCategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        c1 = ModelCategory.objects.create(name="Voltmeter")
        c2 = ModelCategory.objects.create(name="Multimeter")
        c3 = ModelCategory.objects.create(name='Oscilloscope')
        m1 = Model.objects.create(vendor="Fluke",
                                  model_number="86V",
                                  description="High Impedance Voltmeter",
                                  calibration_frequency=timedelta(days=90))
        m2 = Model.objects.create(vendor="Fluke",
                                  model_number="87M",
                                  description="Multimeter with temperature probes",
                                  calibration_frequency=timedelta(days=60))
        m3 = Model.objects.create(vendor="Fluke",
                                  model_number="901C",
                                  description="Portable oscilloscope",
                                  calibration_frequency=timedelta(days=30))
        m1.model_categories.set([c1])
        m2.model_categories.set([c1, c2])
        m3.model_categories.set([c3])
        m1.save()
        m2.save()
        m3.save()

    def test_single_model_for_category(self):
        queryset = ModelCategory.objects.get(name="Multimeter").model_set.all()
        expected_queryset = Model.objects.filter(vendor="Fluke", model_number="87M")
        self.assertEqual(f'{queryset}', f'{expected_queryset}')

    def test_multiple_models_for_category(self):
        queryset = ModelCategory.objects.get(name="Voltmeter").model_set.all()
        expected_queryset = Model.objects.filter(model_categories=1)  # want this to be string
        self.assertEqual(f'{queryset}', f'{expected_queryset}')
