# Generated by Django 4.2.3 on 2023-09-16 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_report', '0013_report_memo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='bad_product_total',
            new_name='bad_product',
        ),
        migrations.RenameField(
            model_name='report',
            old_name='good_product_total',
            new_name='good_product',
        ),
    ]
