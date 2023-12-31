# Generated by Django 4.2.7 on 2023-12-21 12:14

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_rename_renter_id_renteeprofile_rentee_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Administrator",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "joined_on",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2023,
                            12,
                            21,
                            12,
                            14,
                            54,
                            837690,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("users.user",),
            managers=[
                ("admin", django.db.models.manager.Manager()),
            ],
        ),
    ]
