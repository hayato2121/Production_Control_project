# Generated by Django 4.2.3 on 2023-09-12 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_report', '0003_remove_report_end_time_remove_report_start_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='business',
            options={'verbose_name': '業務内容'},
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'verbose_name': '製品情報'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'verbose_name': '日報'},
        ),
    ]
