from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('attendance', '0002_auto_20241126_fix_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='check_in',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='check_out',
            field=models.DateTimeField(null=True),
        ),
    ] 