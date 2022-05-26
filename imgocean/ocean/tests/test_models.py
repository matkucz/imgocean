import os
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from ocean.models import Account, Image, Size, User


class AccountTestCase(TestCase):
    def setUp(self):
        Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )

    def test_account_null_exp_field(self):
        with self.assertRaises(IntegrityError) as context:
            Account.objects.create(
                name='Error', description='', can_generate_exp_links=None
            )
        self.assertTrue('NOT NULL constraint failed' in str(context.exception))

    def test_account_same_name(self):
        with self.assertRaises(IntegrityError) as context:
            Account.objects.create(
                name='Basic', description='', can_generate_exp_links=False
            )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))

class UserTestCase(TestCase):
    def setUp(self):
        Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )

    def test_create_user(self):
        account_type = Account.objects.get(name='Enterprise')
        user = User.objects.create(
            account_type=account_type,
            password='test',
            username='test'
        )
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        account_type = Account.objects.get(name='Enterprise')
        user = User.objects.create(
            account_type=account_type,
            is_superuser=True,
            password='test',
            username='test'
        )
        self.assertTrue(user.is_superuser)


class SizeTestCase(TestCase):
    def setUp(self):
        basic = Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )
        Size.objects.create(
            account_type=basic, height=200
        )

    def test_size_same_height_in_type(self):
        basic = Account.objects.get(name='Basic')
        with self.assertRaises(IntegrityError) as context:
            Size.objects.create(
                account_type=basic, height=200
            )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))

    def test_negative_height(self):
        basic = Account.objects.get(name='Basic')        
        with self.assertRaises(IntegrityError) as context:
            Size.objects.create(
                account_type=basic, height=-1
            )
        self.assertTrue('CHECK constraint failed' in str(context.exception))


class ImageTestCase(TestCase):
    def setUp(self):
        basic = Account.objects.create(
            name='Basic', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Premium', description='', can_generate_exp_links=False
        )
        Account.objects.create(
            name='Enterprise', description='', can_generate_exp_links=True
        )
        Size.objects.create(
            account_type=basic, height=200
        )
        User.objects.create(
            account_type=basic,
            password='test',
            username='test'
        )
    
    def test_add_image(self):
        user = User.objects.get(username='test')
        new_image = Image(
            owner=user,
            exp_after=None
        )
        image_path = os.path.join(os.getcwd(), 'ocean/tests/test.jpeg')
        new_image.img = SimpleUploadedFile(
            name='test.jpeg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg'
        )
        new_image.save()
        self.assertEqual(Image.objects.count(), 1)

    def test_exp_after_validator(self):
        user = User.objects.get(username='test')
        new_image = Image(
            owner=user,
            exp_after=None
        )
        image_path = os.path.join(os.getcwd(), 'ocean/tests/test.jpeg')
        new_image.img = SimpleUploadedFile(
            name='test.jpeg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg'
        )
        with self.assertRaises(ValidationError) as context:
            new_image.exp_after = timezone.now() + timedelta(seconds=0)
            new_image.full_clean()
            new_image.save()
        self.assertTrue('Expiration seconds should be between 300 and 30000.' in str(context.exception))
    
    def test_img_extension_validator(self):
        user = User.objects.get(username='test')
        new_image = Image(
            owner=user,
            exp_after=None
        )
        image_path = os.path.join(os.getcwd(), 'ocean/tests/test.gif')
        new_image.img = SimpleUploadedFile(
            name='test.gif',
            content=open(image_path, 'rb').read(),
            content_type='image/gif'
        )
        with self.assertRaises(ValidationError) as context:
            new_image.full_clean()
        self.assertTrue('Allowed formats are' in str(context.exception))
    
    def test_file_extension_validator(self):
        user = User.objects.get(username='test')
        new_image = Image(
            owner=user,
            exp_after=None
        )
        image_path = os.path.join(os.getcwd(), 'ocean/tests/test.txt')
        new_image.img = SimpleUploadedFile(
            name='test.txt',
            content=open(image_path, 'rb').read(),
            content_type='image/gif'
        )
        with self.assertRaises(ValidationError) as context:
            new_image.full_clean()
        self.assertTrue('Allowed formats are' in str(context.exception))