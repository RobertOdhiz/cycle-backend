# Generated by Django 4.2.7 on 2023-11-25 22:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
    ]
