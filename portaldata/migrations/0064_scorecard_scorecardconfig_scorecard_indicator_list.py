# Generated by Django 4.1 on 2023-04-21 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0063_delete_indicatorscorecardconfig"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScoreCard",
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
                ("scorecard_name", models.CharField(max_length=100)),
                ("scorecard_title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "aggregation",
                    models.CharField(
                        blank=True,
                        choices=[("avg", "Average"), ("sum", "Total")],
                        max_length=10,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Scorecards",
                "ordering": ["pk"],
            },
        ),
        migrations.CreateModel(
            name="ScoreCardConfig",
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
                (
                    "extra_calculation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("numerator", "Numerator"),
                            ("denominator", "Denominator"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portaldata.indicator",
                    ),
                ),
                (
                    "scorecard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portaldata.scorecard",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Scorecard Configuration",
                "ordering": ["scorecard__pk", "pk"],
            },
        ),
        migrations.AddField(
            model_name="scorecard",
            name="indicator_list",
            field=models.ManyToManyField(
                through="portaldata.ScoreCardConfig", to="portaldata.indicator"
            ),
        ),
    ]
