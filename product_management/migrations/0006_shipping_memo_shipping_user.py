# Generated by Django 4.2.3 on 2023-09-24 01:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product_management', '0005_remove_shipping_stock_shipping_stock1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='引き継ぎメモ'),
        ),
        migrations.AddField(
            model_name='shipping',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー名'),
        ),
    ]
