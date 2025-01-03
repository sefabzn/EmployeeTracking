# Generated by Django 4.2.7 on 2024-11-27 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notification_notification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='related_object_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='related_object_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('late_checkin', 'Late Check-in'), ('missing_checkout', 'Missing Check-out'), ('absent', 'Absent'), ('leave_balance', 'Leave Balance Alert'), ('leave_request', 'Leave Request'), ('monthly_report', 'Monthly Report')], max_length=20),
        ),
    ]
