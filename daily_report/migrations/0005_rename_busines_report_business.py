# Generated by Django 4.2.3 on 2023-09-12 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_report', '0004_alter_business_options_alter_products_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='busines',
            new_name='business',
        ),
    ]
