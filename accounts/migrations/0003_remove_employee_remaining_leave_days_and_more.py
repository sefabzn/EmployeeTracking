# Generated by Django 4.2.7 on 2024-11-25 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_role_alter_employee_options_remove_employee_username_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='remaining_leave_days',
        ),
        migrations.AddField(
            model_name='employee',
            name='annual_leave_days',
            field=models.FloatField(default=15.0),
        ),
        migrations.AddField(
            model_name='employee',
            name='used_leave_days',
            field=models.FloatField(default=0.0),
        ),
    ]