# Generated by Django 3.0.1 on 2020-01-01 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toei', '0015_getcourt'),
    ]

    operations = [
        migrations.CreateModel(
            name='OddsCourt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4, verbose_name='年')),
                ('month', models.CharField(max_length=2, verbose_name='月')),
                ('day', models.CharField(max_length=2, verbose_name='日付')),
                ('from_time', models.CharField(max_length=2, verbose_name='開始時間')),
                ('to_time', models.CharField(max_length=2, verbose_name='終了時間')),
                ('court', models.CharField(max_length=1, verbose_name='コート')),
                ('odds', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='倍率')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('delete_flg', models.CharField(default=0, max_length=1, verbose_name='削除フラグ')),
            ],
            options={
                'verbose_name_plural': 'OddsCourt',
                'db_table': 'odds_court',
            },
        ),
    ]
