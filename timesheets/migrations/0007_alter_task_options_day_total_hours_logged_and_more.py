# Generated by Django 5.2.3 on 2025-06-26 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheets', '0006_task'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['day__day_date', 'task_type']},
        ),
        migrations.AddField(
            model_name='day',
            name='total_hours_logged',
            field=models.FloatField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('day', 'task_type')},
        ),
    ]
