# Generated by Django 4.2.3 on 2023-09-17 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0002_alter_molding_options_alter_shipping_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='delivery',
            options={'verbose_name': '納品先'},
        ),
    ]
