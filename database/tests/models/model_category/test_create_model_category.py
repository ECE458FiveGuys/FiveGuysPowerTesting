from django.test import TestCase
from database.models import ModelCategory
from django.core.exceptions import ValidationError


class CreateModelCategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ModelCategory.objects.create(name="Voltmeter")

    def test_name_field(self):
        model_category = ModelCategory.objects.get(name="Voltmeter")
        expected_object_name = "Voltmeter"
        self.assertEqual(f'{model_category.name}', expected_object_name)

    def test_string_representation(self):
        model_category = ModelCategory.objects.get(name="Voltmeter")
        expected_object_name = "Voltmeter"
        self.assertEqual(f'{model_category}', expected_object_name)

    def test_empty_string_name(self):
        model_category = ModelCategory.objects.create(name="")
        with self.assertRaises(ValidationError):
            model_category.full_clean()

    def test_name_with_spaces(self):
        model_category = ModelCategory.objects.create(name="Test Bank")
        with self.assertRaises(ValidationError):
            model_category.full_clean()
