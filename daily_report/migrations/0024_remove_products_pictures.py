# Generated by Django 4.2.3 on 2023-09-30 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_report', '0023_alter_report_good_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='pictures',
        ),
    ]