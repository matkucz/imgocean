from django.conf import settings
from django.core.management.base import BaseCommand
from ocean.models import Account, User

class Command(BaseCommand):
    help = 'Create default admin account'

    def handle(self, *args, **kwargs):
        account_type = Account.objects.get(name='Enterprise')
        admin = settings.DEFAULT_ADMIN
        username = admin['USERNAME']
        password = admin['PASSWORD']
        admin_model = User.objects.create_superuser(email='', username=username, password=password, account_type=account_type)
        admin_model.is_active = True
        admin_model.is_admin = True
        admin_model.save()
        self.stdout.write(self.style.SUCCESS("Successfully created admin account"))