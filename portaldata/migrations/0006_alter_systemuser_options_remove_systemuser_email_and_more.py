# Generated by Django 4.1 on 2022-11-04 06:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portaldata", "0005_alter_exchangeratedata_exchange_rate_date"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="systemuser",
            options={"ordering": ["user__first_name", "user__last_name"]},
        ),
        migrations.RemoveField(
            model_name="systemuser",
            name="email",
        ),
        migrations.RemoveField(
            model_name="systemuser",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="systemuser",
            name="last_name",
        ),
        migrations.AddField(
            model_name="systemuser",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
