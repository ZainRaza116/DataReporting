# Generated by Django 4.2.2 on 2023-07-10 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0014_gamesummary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="game",
            name="daily_report",
        ),
    ]
