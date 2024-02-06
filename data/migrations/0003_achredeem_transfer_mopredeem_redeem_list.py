# Generated by Django 4.2.2 on 2023-06-11 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0002_alter_catogorie_id_alter_mopredeem_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACHRedeem",
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
                    "customer",
                    models.CharField(max_length=255, verbose_name="Customer Name"),
                ),
                (
                    "amount",
                    models.FloatField(
                        blank=True, default=0.0, null=True, verbose_name="Redeem Amount"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transfer",
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
                    "customer",
                    models.CharField(max_length=255, verbose_name="Customer Name"),
                ),
                (
                    "amount",
                    models.FloatField(
                        blank=True, default=0.0, null=True, verbose_name="Redeem Amount"
                    ),
                ),
                (
                    "from_game",
                    models.CharField(max_length=255, verbose_name="From Game"),
                ),
                ("to_game", models.CharField(max_length=255, verbose_name="To Game")),
            ],
        ),
        migrations.AddField(
            model_name="mopredeem",
            name="redeem_list",
            field=models.ManyToManyField(to="data.mopredeem"),
        ),
    ]