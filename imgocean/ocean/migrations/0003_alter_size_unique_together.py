# Generated by Django 4.0.4 on 2022-05-26 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocean', '0002_alter_account_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='size',
            unique_together={('account_type', 'height')},
        ),
    ]