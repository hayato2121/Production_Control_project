# Generated by Django 4.2.3 on 2023-09-25 04:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0007_alter_shipping_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipping',
            name='shipments_required',
            field=models.IntegerField(verbose_name='出荷必要数'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='stock1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock1_set', to='product_management.stock', verbose_name='使用在庫1'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='stock2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock2_set', to='product_management.stock', verbose_name='使用在庫2'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='stock3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock3_set', to='product_management.stock', verbose_name='使用在庫3'),
        ),
    ]