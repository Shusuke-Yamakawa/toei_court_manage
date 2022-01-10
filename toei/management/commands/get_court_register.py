import re
import datetime

from django.db.models import Q
from django.conf import settings

from selenium.common.exceptions import NoSuchElementException
from toei.management.commands.Lib.utility import Utility

from .command_super import CommandSuper
from ...models import *


class Command(CommandSuper):
    help = "GetCourtRegister Toei"
    TARGET_NOTE = "検査対象"

    def handle(self, *args, **options):
        try:
            msg = []
            toeis = Toei.objects.raw(
                        """
                        SELECT * FROM toei
                        WHERE user_id=%s AND available_flg='1'
                        AND
                        (note=%s
                         OR
                         card_id IN (SELECT card_id FROM get_court WHERE delete_flg = '0')
                         )
                        ;
                        """
                        ,[Utility.USER_SHU, self.TARGET_NOTE])
            for toei in toeis:
                msg.append(super().loginProc(toei.card_id, toei.password))
                self.driver.find_element_by_id('goRsvStatusList').click()
                self.driver.get_screenshot_as_file(str(settings.CAPTURE_DIRS) +  "_list.png")
                # 一度ユーザーに紐づくレコードを削除し、以下で再登録する(22日になるまでは翌月分は削除しない）
                now_month = datetime.datetime.now().month
                last_month = 12 if now_month == 1 else now_month - 1
                now_day = datetime.datetime.now().day;
                if 22 > now_day:
                    GetCourt.objects.filter(Q(card_id=toei.card_id), Q(month__in=[last_month, now_month]), \
                                            Q(use_flg="0") | Q(month=last_month) | Q(month=now_month, day__lt=now_day)).delete()
                else:
                    GetCourt.objects.filter(Q(card_id=toei.card_id), Q(use_flg="0") | Q(month=last_month) | Q(month=now_month, day__lt=now_day)).delete()
                msg.append(self.get_info(toei.card_id))
                # 次のページ
                while True:
                    try:
                        self.driver.find_element_by_id('goNextPager').click()
                        msg.append(self.get_info(toei.card_id))
                    except NoSuchElementException:
                        # 次のページが押せなくなったらループから抜ける
                        break
                self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()

        except NoSuchElementException as e:
            msg.append(super().error_proc(e))

        finally:
            super().finally_proc(''.join(msg))

    def get_info(self, id):
        web_elements = self.driver.find_elements_by_id('ymdLabel')
        msg = []
        for i in range(len(web_elements)):
            date = self.driver.find_elements_by_id('ymdLabel')[i].text
            from_time = self.driver.find_elements_by_id('stimeLabel')[i].text
            to_time = self.driver.find_elements_by_id('etimeLabel')[i].text
            court_nm = self.driver.find_elements_by_id('bnamem')[i].text
            msg.append("\n" + date[5:-1] + " " \
                   + from_time[:-1] + "-" \
                   + to_time[:-1] + " " \
                   + court_nm[:-2])
            # DB登録用に変換
            month = re.match(r'.*年(\d+)月.*', date).group(1)
            day = re.match(r'.*月(\d+)日.*', date).group(1)
            from_time_db = re.match(r'(\d+)', from_time).group(1)
            to_time_db = re.match(r'(\d+)', to_time).group(1)
            court_key = [k for k, v in dict(COURT_CHOICES).items() if v == court_nm]
            court_id = court_key[0] if court_key else 9
            # DBに登録する
            get_court = GetCourt.objects.filter(card_id=Toei(id), year=date[0:4], month=month, day=day, \
                                     from_time=from_time_db, to_time=to_time_db, court=court_id, use_flg="1")
            if get_court:
                msg.append("\n" + "【使用予定】")
            else:
                get_court_new = GetCourt(card_id=Toei(id), year=date[0:4], month=month, day=day, \
                                         from_time=from_time_db, to_time=to_time_db, court=court_id)
                get_court_new.save()

        return ''.join(msg)