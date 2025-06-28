from django.test import TestCase
from ecomapp.models import *

class TestCategoriesModel(TestCase):

    def setup(self):
        self.data1 = Category.objects.create(cat_name = 'django', cat_slug = 'django')

    
    def test_category_model_entry(self):
        """
        Test Category model data insertion/types/field attributes
        """
        data = self.data1
        self.assertTrue(isinstance(data, Category))
