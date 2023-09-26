# Generated by Django 4.2.3 on 2023-09-24 00:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0004_alter_delivery_delivery_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipping',
            name='stock',
        ),
        migrations.AddField(
            model_name='shipping',
            name='stock1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock1_set', to='product_management.stock', verbose_name='必要ロッドナンバー1'),
        ),
        migrations.AddField(
            model_name='shipping',
            name='stock2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock2_set', to='product_management.stock', verbose_name='必要ロッドナンバー2'),
        ),
        migrations.AddField(
            model_name='shipping',
            name='stock3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock3_set', to='product_management.stock', verbose_name='必要ロッドナンバー3'),
        ),
    ]