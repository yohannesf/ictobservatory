# Generated by Django 4.1 on 2022-11-16 08:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portaldata", "0014_alter_currency_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="systemuser",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
