# Generated by Django 4.2.3 on 2023-09-18 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daily_report', '0018_alter_report_business_alter_report_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='作業状況'),
        ),
    ]