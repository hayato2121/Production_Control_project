# Generated by Django 4.2.3 on 2023-09-17 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0003_alter_delivery_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='molding',
            old_name='bat_molding',
            new_name='bad_molding',
        ),
    ]
