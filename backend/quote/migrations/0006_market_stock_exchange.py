# Generated by Django 3.2.8 on 2021-10-25 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quote', '0005_auto_20211025_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='stock_exchange',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='quote.stockexchange'),
            preserve_default=False,
        ),
    ]
