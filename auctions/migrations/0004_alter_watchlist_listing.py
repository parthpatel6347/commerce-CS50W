# Generated by Django 4.0 on 2022-01-03 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='Listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing', to='auctions.listing'),
        ),
    ]
