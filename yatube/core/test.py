from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()

class CoreTestClass(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()

    def test_error_page(self):
        response = self.client.get('/page_no_exist/')
        used_template = 'core/404.html'
        self.assertTemplateUsed(response, used_template)