# Generated by Django 4.0 on 2022-01-15 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_type_user_account_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='account_type',
            new_name='type',
        ),
    ]
