from accounts.models import CustomUser
from django.db import models

AVAILABLE_CHOICES = (('0', '無効'), ('1', '有効'))
COURT_CHOICES = (('0', '府中の森公園'), ('1', '小金井公園'), ('2', '野川公園'), ('3', '井の頭恩賜公園'), ('4', '武蔵野中央公園'), ('5', '東大和南公園'))
USE_CHOICES = (('0', '未確定'), ('1', '確定'))

class Toei(models.Model):
    """都営カードモデル"""

    card_id = models.CharField(verbose_name='都営カードID', max_length=8, primary_key=True)
    password = models.CharField(verbose_name='都営カードパスワード', max_length=8)
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT)
    user_nm_kj = models.CharField(verbose_name='ユーザー名漢字', max_length=80, null=True)
    user_nm_kn = models.CharField(verbose_name='ユーザー名カナ', max_length=80)
    give_nm = models.CharField(verbose_name='カード提供者', max_length=80)
    expire_date = models.DateField(verbose_name='有効期限', null=True)
    available_flg = models.CharField(verbose_name='有効フラグ', choices=AVAILABLE_CHOICES, max_length=1, default=1)
    share_team = models.CharField(verbose_name='共有チーム', max_length=80, null=True)
    note = models.TextField(verbose_name='備考', null=True)

    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    delete_flg = models.CharField(verbose_name='削除フラグ', max_length=1, default=0)

    class Meta:
        db_table = 'toei'
        verbose_name_plural = 'Toei'

    def __str__(self):
        return '{0} {1}'.format(self.card_id, self.user_nm_kn)

class Draw(models.Model):
    """抽選モデル"""

    card_id = models.ForeignKey(Toei, verbose_name='都営カードID', db_column='card_id', on_delete=models.PROTECT)
    year = models.IntegerField(verbose_name='年')
    month = models.IntegerField(verbose_name='月')
    day = models.IntegerField(verbose_name='日付')
    from_time = models.IntegerField(verbose_name='開始時間')
    to_time = models.IntegerField(verbose_name='終了時間')
    court = models.CharField(verbose_name='コート', choices=COURT_CHOICES, max_length=1, default=1)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    delete_flg = models.CharField(verbose_name='削除フラグ', max_length=1, default=0)

    draw_conf_flg = models.CharField(verbose_name='抽選確定フラグ', max_length=1, default=0)

    class Meta:
        db_table = 'draw'
        verbose_name_plural = 'Draw'

    def __str__(self):
        return '{0} {1} {2} {3} {4}'.format(self.card_id, self.year, self.month, self.day, self.from_time)

class GetCourt(models.Model):
    """取得コートモデル"""

    card_id = models.ForeignKey(Toei, verbose_name='都営カードID', db_column='card_id', on_delete=models.PROTECT)
    year = models.IntegerField(verbose_name='年')
    month = models.IntegerField(verbose_name='月')
    day = models.IntegerField(verbose_name='日付')
    from_time = models.IntegerField(verbose_name='開始時間')
    to_time = models.IntegerField(verbose_name='終了時間')
    court = models.CharField(verbose_name='コート', choices=COURT_CHOICES, max_length=1, default=1)
    use_flg = models.CharField(verbose_name='使用フラグ', choices=USE_CHOICES, max_length=1, default=0)

    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    delete_flg = models.CharField(verbose_name='削除フラグ', max_length=1, default=0)

    class Meta:
        db_table = 'get_court'
        verbose_name_plural = 'GetCourt'

    def __str__(self):
        return '{0} {1} {2} {3} {4}'.format(self.card_id, self.year, self.month, self.day, self.from_time)

class OddsCourt(models.Model):
    """コート倍率モデル"""

    year = models.IntegerField(verbose_name='年')
    month = models.IntegerField(verbose_name='月')
    day = models.IntegerField(verbose_name='日付')
    from_time = models.IntegerField(verbose_name='開始時間')
    to_time = models.IntegerField(verbose_name='終了時間')
    court = models.CharField(verbose_name='コート', choices=COURT_CHOICES, max_length=1, default=1)
    odds = models.DecimalField(verbose_name='倍率',max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    delete_flg = models.CharField(verbose_name='削除フラグ', max_length=1, default=0)

    empty_court = models.IntegerField(verbose_name='当選可能数', default=0)
    apply_court = models.IntegerField(verbose_name='申込件数数', default=0)

    class Meta:
        db_table = 'odds_court'
        verbose_name_plural = 'OddsCourt'

    def __str__(self):
        return '{0} {1} {2} {3} {4}'.format(self.year, self.month, self.day, self.from_time, self.court)