# Generated by Django 4.0 on 2022-01-12 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_currency_ewallet_user_type_user_fullname_withdrawal_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.DecimalField(decimal_places=2, max_digits=15)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
                ('user_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.ewallet')),
            ],
        ),
    ]
