# Generated by Django 4.2.1 on 2023-12-10 08:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account_app', '0005_alter_driverdocket_shiftdate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverdocket',
            name='shiftDate',
            field=models.DateField(default=datetime.datetime(2023, 12, 10, 8, 21, 46, 374343, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='holcimdocket',
            name='loadComplete',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='holcimdocket',
            name='status',
            field=models.CharField(default='', max_length=200),
        ),
    ]
