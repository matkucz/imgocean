import os
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ocean.models import Account, Image, Size, User
from ocean.views import SignupView, ImageUploadView, ImageDetailView

class UserTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )

    def test_signup_wrong_acocunt_type(self):
        request = self.factory.post('/api/signup/', {
            'username': 'test',
            'password': 'test',
            'account_type': 4
        })
        response = SignupView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_signup_wrong_username(self):
        datas = [
            {
                'username': '',
                'password': 'sss',
                'account_type': 1
            },
            {
                'username': [],
                'password': 'sss',
                'account_type': 1
            },
            {
                'username': '   ',
                'password': 'sss',
                'account_type': 1
            }
        ]
        for data in datas:
            request = self.factory.post('/api/signup/', data)
            response = SignupView.as_view()(request)
            self.assertEqual(response.status_code, 400)

    def test_signup_wrong_password(self):
        datas = [
            {
                'username': 'test',
                'password': '    ',
                'account_type': 1
            },
            {
                'username': 'test',
                'password': '',
                'account_type': 1
            }
        ]
        for data in datas:
            request = self.factory.post('/api/signup/', data)
            response = SignupView.as_view()(request)
            self.assertEqual(response.status_code, 400)
    
    def test_create_two_admin_accounts(self):
        request = self.factory.post('/api/signup/', {
            'username': 'admin',
            'password': 'admin',
            'account_type': 1
        })
        response = SignupView.as_view()(request)
        self.assertEqual(response.status_code, 201)

        request = self.factory.post('/api/signup/', {
            'username': 'admin',
            'password': 'admin',
            'account_type': 1
        })
        response = SignupView.as_view()(request)
        self.assertEqual(response.status_code, 400)

class ImageTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        basic = Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        premium = Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        enterprise = Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )
        Size.objects.create(
            account_type=basic, height=200
        )
        Size.objects.create(
            account_type=premium, height=200
        )
        Size.objects.create(
            account_type=premium, height=400
        )
        Size.objects.create(
            account_type=premium, height=0
        )
        Size.objects.create(
            account_type=enterprise, height=200
        )
        Size.objects.create(
            account_type=enterprise, height=400
        )
        Size.objects.create(
            account_type=enterprise, height=0
        )
        self.basic_user = User.objects.create(
            username='test',
            password='test',
            is_superuser=False,
            account_type=basic
        )
        self.premium_user = User.objects.create(
            username='test_2',
            password='test',
            is_superuser=False,
            account_type=premium
        )
        image_path = os.path.join(os.getcwd(), 'ocean/tests/test.jpeg')
        self.image = SimpleUploadedFile(
            name='test.jpeg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg'
        )
    def test_anonymous_get_images(self):
        request = self.factory.get('/api/images/')
        response = ImageUploadView.as_view()(request)
        self.assertEqual(response.status_code, 401)
    
    def test_anonymous_post_image(self):
        request = self.factory.post(
            '/api/images/',
            {
                'img': self.image,                
            }, 
            format='multipart'
        )
        response = ImageUploadView.as_view()(request)
        self.assertEqual(response.status_code, 401)

    def test_post_image(self):
        request = self.factory.post(
            '/api/images/',
            {
                'img': self.image,                
            }, 
            format='multipart'
        )
        force_authenticate(request, user=self.basic_user)
        response = ImageUploadView.as_view()(request)
        self.assertEqual(response.status_code, 201)

    def test_post_and_get_images(self):
        pass

    def test_invalid_image(self):
        pass

    def test_post_exp_image(self):
        pass
    
    def test_get_image_wrong_size(self):
        request = self.factory.post(
            '/api/images/',
            {
                'img': self.image,                
            }, 
            format='multipart'
        )
        force_authenticate(request, user=self.basic_user)
        response = ImageUploadView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        image_address = response.data['th_200_px']
        image, size = image_address.split('?')
        image_request = self.factory.get(
            f'{image}?size=300'
        )
        img_response = ImageUploadView.as_view()(image_request)
        self.assertEqual(img_response.status_code, 401)

    def test_get_image_invalid_size_param(self):
        request = self.factory.post(
            '/api/images/',
            {
                'img': self.image,                
            }, 
            format='multipart'
        )
        force_authenticate(request, user=self.basic_user)
        response = ImageUploadView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        image_address = response.data['th_200_px']
        image, size = image_address.split('?')
        # size is empty
        image_request = self.factory.get(
            f'{image}?size='
        )
        img_response = ImageUploadView.as_view()(image_request)
        self.assertEqual(img_response.status_code, 401)
        # size is string
        image_request = self.factory.get(
            f'{image}?size=sss'
        )
        img_response = ImageUploadView.as_view()(image_request)
        self.assertEqual(img_response.status_code, 401)
        # non-alphanumeric size
        image_request = self.factory.get(
            f'{image}?size=""'
        )
        img_response = ImageUploadView.as_view()(image_request)
        self.assertEqual(img_response.status_code, 401)

    def test_get_exp_image(self):
        pass
