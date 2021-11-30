# Generated by Django 3.2.8 on 2021-10-25 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quote', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True)),
                ('fullname', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BondAdditionalInfo',
            fields=[
                ('ticker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='quote.ticker')),
                ('short_name', models.CharField(max_length=1000)),
                ('code_isin', models.CharField(max_length=100, unique=True)),
                ('gov_reg_number', models.CharField(max_length=1000)),
                ('issue_size', models.FloatField()),
                ('lot_size', models.FloatField()),
                ('lot_value', models.FloatField()),
                ('min_step', models.FloatField()),
                ('list_level', models.CharField(max_length=1000)),
                ('status', models.CharField(max_length=1000)),
                ('coupon_percent', models.FloatField()),
                ('coupon_period', models.FloatField()),
                ('coupon_value', models.FloatField()),
                ('maturity_date', models.DateTimeField()),
                ('next_coupon_date', models.DateTimeField()),
                ('accumulated_coupon_yield', models.FloatField()),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.currency')),
            ],
        ),
    ]
