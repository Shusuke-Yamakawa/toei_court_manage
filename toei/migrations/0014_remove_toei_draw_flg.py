# Generated by Django 3.0.1 on 2020-01-01 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toei', '0013_auto_20200101_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toei',
            name='draw_flg',
        ),
    ]