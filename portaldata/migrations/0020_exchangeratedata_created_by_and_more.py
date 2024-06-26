# Generated by Django 4.1 on 2022-11-19 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portaldata", "0019_organisation_organisation_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangeratedata",
            name="created_by",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="ExchangeRate_Created_By",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="created_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="last_update",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="reporting_year",
            field=models.CharField(default=2022, max_length=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="submitted",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")],
                default=False,
                verbose_name="Is Submitted ? ",
            ),
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="updated_by",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="ExchangeRate_Last_Updated_By",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangeratedata",
            name="validated",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")],
                default=False,
                verbose_name="Is validated ? ",
            ),
        ),
    ]
