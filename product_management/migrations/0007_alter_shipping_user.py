# Generated by Django 4.2.3 on 2023-09-24 06:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product_management', '0006_shipping_memo_shipping_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipping',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='作業者名'),
        ),
    ]
