import csv
import logging

from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
import requests

from .command_super import CommandSuper
from ...models import Draw
from ...models import Toei
from .Lib.utility import Utility
logger = logging.getLogger(__name__)

class Command(CommandSuper):
    help = "DrawInput Toei"

    """"
    切り替えること
    　user_id
    　Line通知
    　input.csv
    """
    def handle(self, *args, **options):

        # CSVファイルパス
        csv_file = settings.CSV_FILE_INPUT
        user_id = Utility.USER_JOIAS

        try:
            msg = []
            warnMsg = []

            with open(csv_file, encoding="utf_8") as f:
                reader = csv.reader(f)  # readerオブジェクトを作成
                header = next(reader)  # 最初の一行をヘッダーとして取得

                # 行ごとのリストを処理する
                for itemInfo in reader:
                    # ディクショナリ化（タプルリスト化後に変換）
                    items = dict([(header[x], itemInfo[x]) for x in range(len(header))])

                    # オンバッチにしてユーザーごとに切り替えられるようにする
                    # Drawテーブルに存在しないデータを取得する
                    toeis = Toei.objects.raw(
                        """
                        SELECT * FROM toei
                        WHERE user_id=%s AND available_flg='1' AND delete_flg = '0'
                        AND card_id NOT IN(SELECT card_id FROM draw WHERE year = %s AND month = %s AND delete_flg='0')
                        order by created_at LIMIT %s ;
                        """
                        ,[user_id, self.year, self.month, items['Number']])
                    for toei in toeis:

                        # ログイン処理
                        msg.append(super().loginProc(toei.card_id, toei.password))

                        # 期限切れ警告
                        warnMsg.append(super().warnExpired(toei, False))

                        try:
                            self.driver.find_element_by_id('goLotSerach').click()
                        except NoSuchElementException:
                            msg.append("\n" + "抽選失敗")
                            self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()
                            continue

                        # メイン処理
                        self.draw_proc(items)

                        # 後処理
                        msg.append(self.draw_proc_after(toei, items))

        except Exception as e:
            msg.append(super().error_proc(e))

        finally:
            # Joiasに期限切れメッセージを送る
            line_notify_api = 'https://notify-api.line.me/api/notify'
            line_notify_token = ""
            if warnMsg:
                warnSend = ''.join(warnMsg)
                logger.warning(warnSend)
                if user_id == Utility.USER_JOIAS:
                    line_notify_token += 'kKnuPzReJ5A9Ij7yVhORGeAkScmgl9u9UAVeSXqtH0l'
                else:
                    line_notify_token += 'QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva'
                payload = {'message': warnSend}
                headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
                line_notify = requests.post(line_notify_api, data=payload, headers=headers)
            super().finally_proc(''.join(msg))

    def input_on_line(self, **kwargs):
        try:
            msg = []
            toeis = Toei.objects.raw(
                """
                SELECT * FROM toei
                WHERE user_id=%s AND available_flg='1'
                AND card_id NOT IN(SELECT card_id FROM draw WHERE year = %s AND month = %s AND delete_flg='0')
                order by created_at LIMIT %s ;
                """
                , [kwargs.get('user_id'), kwargs.get('year'), kwargs.get('month'), int(kwargs.get('add_num'))])
            for toei in toeis:
                # ログイン処理
                msg.append(super().loginProc(toei.card_id, toei.password))
                self.driver.find_element_by_id('goLotSerach').click()
                # メイン処理
                self.draw_proc(kwargs)
                # 後処理
                msg.append(self.draw_proc_after(toei, kwargs))

        except Exception as e:
            msg.append(super().error_proc(e))

        finally:
            super().finally_proc(''.join(msg))

    def draw_proc(self, items):
        self.driver.find_element_by_id('goFavLotList').click()
        self.driver.find_element_by_xpath(
            "//input[@type='radio' and @value='{0}']".format(items['Court'])).click()
        self.driver.find_element_by_id('doLotApp').click()
        self.applyApp(items)

        # 2回目の抽選
        self.driver.find_element_by_id('doDateSearch').click()
        self.applyApp(items)

    def applyApp(self, items):
        self.driver.find_element_by_link_text(items['Day']).click()
        target_time = items['FromTime'] + '00_' + items['ToTime'] + '00'
        self.driver.find_element_by_xpath("//input[@value='{0}']".format(target_time)).click()
        self.driver.find_element_by_xpath("//input[@value='申込みを確定する']").click()
        self.driver.find_element_by_xpath("//input[@value='抽選を申込む']").click()
        self.driver.switch_to_alert().accept()

    def draw_proc_after(self, toei, items):
        draw = Draw(card_id=Toei(card_id=toei.card_id), year=self.year, month=self.month, day=items['Day'], \
                    from_time=items['FromTime'], to_time=items['ToTime'], court=items['Court'])
        draw.save()
        msg = "\n" + self.driver.find_element_by_id("bgcdnamem").text
        msg += "\n" + self.driver.find_element_by_id(
            "targetLabel").text + " " + self.driver.find_element_by_id("timeLabel").text
        msg += "\n" + "件数" + self.driver.find_element_by_id("totalCount").text
        self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()
        return msg
