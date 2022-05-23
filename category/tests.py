from django.test import TestCase

# Create your tests here.
from .models import category

# Create your tests here.
class CategoryTestCase(TestCase):
    def setUp(self):
        category.objects.create(category_name='Paracetamol',slug='Paracetamol', description='Test',cat_image='image')       

    
    def test_product_test(self):
        name1= category.objects.get(category_name='Paracetamol')
       
        self.assertEqual(name1.category_name,'Paracetamol')