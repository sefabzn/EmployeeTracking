# Generated by Django 4.2.7 on 2024-11-25 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='notification',
            name='title',
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('late_checkin', 'Late Check-in'), ('leave_request', 'Leave Request'), ('other', 'Other')], default='other', max_length=20),
        ),
    ]
