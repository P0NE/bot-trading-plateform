# Generated by Django 4.0.4 on 2024-10-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gridbot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gridconfig',
            name='grid_step',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gridconfig',
            name='symbol',
            field=models.CharField(default='BTCUSDT', max_length=10),
        ),
        migrations.AlterField(
            model_name='gridconfig',
            name='grid_levels',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='gridconfig',
            name='order_size',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='trade',
            name='quantity',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
    ]
