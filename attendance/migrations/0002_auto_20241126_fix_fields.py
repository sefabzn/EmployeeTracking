from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='work_hours',
            field=models.DecimalField(max_digits=5, decimal_places=2, default=0),
        ),
    ]