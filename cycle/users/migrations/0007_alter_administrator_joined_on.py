# Generated by Django 4.2.7 on 2023-12-21 12:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_administrator"),
    ]

    operations = [
        migrations.AlterField(
            model_name="administrator",
            name="joined_on",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]