# Generated by Django 4.2.1 on 2023-12-14 07:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Account_app', '0012_alter_driverdocket_shiftdate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Appointment_app', '0002_remove_appointment_driver_remove_appointment_truckno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='Created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='Created_time',
            field=models.TimeField(default=datetime.datetime(2023, 12, 14, 7, 17, 47, 93219, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='End_Date_Time',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 14, 7, 17, 47, 92413, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='Origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Account_app.baseplant'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='Start_Date_Time',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 14, 7, 17, 47, 92413, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='Status',
            field=models.CharField(choices=[('Unassigned', 'Unassigned'), ('Assigned', 'Assigned'), ('Dispatched', 'Dispatched'), ('InProgress', 'InProgress'), ('Incomplete', 'Incomplete'), ('Complete', 'Complete'), ('Cancelled', 'Cancelled')], default='incomplete', max_length=20),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='report_to_origin',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 14, 7, 17, 47, 92413, tzinfo=datetime.timezone.utc)),
        ),
    ]
