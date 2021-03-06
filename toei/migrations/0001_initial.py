# Generated by Django 3.0.1 on 2019-12-30 03:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Toei',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_id', models.CharField(max_length=8, verbose_name='都営カードID')),
                ('password', models.CharField(max_length=8, verbose_name='都営カードパスワード')),
                ('user_nm_kj', models.CharField(max_length=80, null=True, verbose_name='ユーザー名漢字')),
                ('user_nm_kn', models.CharField(max_length=80, verbose_name='ユーザー名カナ')),
                ('give_nm', models.CharField(max_length=80, verbose_name='カード提供者')),
                ('expire_date', models.DateField(null=True, verbose_name='有効期限')),
                ('available_flg', models.CharField(default=1, max_length=1, verbose_name='有効フラグ')),
                ('share_team', models.CharField(max_length=80, null=True, verbose_name='共有チーム')),
                ('note', models.TextField(null=True, verbose_name='備考')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('delete_flg', models.CharField(default=0, max_length=1, verbose_name='削除フラグ')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name_plural': 'Toei',
            },
        ),
    ]
