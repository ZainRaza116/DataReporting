# Generated by Django 4.2.2 on 2023-07-04 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0012_remove_transfer_daily_report_game_daily_report"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="daily_report",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="data.dailyreport",
            ),
        ),
    ]
