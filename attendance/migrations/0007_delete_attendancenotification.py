# Generated by Django 4.2.7 on 2024-11-27 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0006_alter_attendance_check_in_alter_attendance_check_out'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AttendanceNotification',
        ),
    ]
