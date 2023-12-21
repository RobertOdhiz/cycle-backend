# Generated by Django 4.2.7 on 2023-12-21 14:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("components", "0002_bike_brand_bike_rent_price"),
    ]

    operations = [
        migrations.RenameField(
            model_name="history",
            old_name="event_type",
            new_name="rental_status",
        ),
        migrations.AddField(
            model_name="wallet",
            name="last_top_up",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
