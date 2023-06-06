# Generated by Django 4.1 on 2023-06-03 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_alter_systemuser_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="systemuser",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[("FP", "Focal Point Person"), ("DE", "Data Entry Person")],
                default="FP",
                max_length=150,
            ),
        ),
    ]