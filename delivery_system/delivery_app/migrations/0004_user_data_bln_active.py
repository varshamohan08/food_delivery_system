# Generated by Django 4.2.7 on 2023-11-18 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0003_user_data_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_data',
            name='bln_active',
            field=models.BooleanField(default=True),
        ),
    ]
