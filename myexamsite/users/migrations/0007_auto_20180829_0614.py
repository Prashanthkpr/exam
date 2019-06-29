# Generated by Django 2.1 on 2018-08-29 06:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20180829_0544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(message='Enter valid phone number', regex='(0|+91)?[789][0-9]{9}')]),
        ),
    ]
