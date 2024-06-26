# Generated by Django 4.1 on 2022-12-17 12:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portaldata", "0032_alter_indicatordata_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="indicatordatavalidationhistory",
            options={
                "ordering": ["-last_update"],
                "verbose_name_plural": "Indicator Data Validation History",
            },
        ),
        migrations.AlterField(
            model_name="exchangeratedata",
            name="exchange_rate",
            field=models.FloatField(
                help_text="Exchange rate of 1 USD to local currency"
            ),
        ),
        migrations.CreateModel(
            name="GeneralIndicator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("indicator_label", models.CharField(max_length=200)),
                ("indicator_value", models.CharField(max_length=200)),
                ("reporting_year", models.CharField(max_length=6)),
                ("last_update", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="GeneralIndicator_Last_Updated_By",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
