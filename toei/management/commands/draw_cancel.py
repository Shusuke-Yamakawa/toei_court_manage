import csv
from django.conf import settings
from .command_super import CommandSuper
from .Lib.utility import Utility
from ...models import Draw


class Command(CommandSuper):
    help = "DrawCancel Toei"

    """"
    切り替えること
      user_id
      Line通知
      cancel.csv
    """
    def handle(self, *args, **options):

        # CSVファイルパス
        csv_file = settings.CSV_FILE_CANCEL
        user_id = '1'

        try:
            msg = []

            with open(csv_file, encoding="utf_8") as f:
                reader = csv.reader(f)  # readerオブジェクトを作成
                header = next(reader)  # 最初の一行をヘッダーとして取得

                # 行ごとのリストを処理する
                for itemInfo in reader:
                    # ディクショナリ化（タプルリスト化後に変換）
                    items = dict([(header[x], itemInfo[x]) for x in range(len(header))])
                    year, month = Utility.get_next_year_month()
                    # ユーザーごとに切り替えられるようにする
                    draws = Draw.objects.filter(card_id__user=user_id, year=year, month=month, day=items['Day'], \
                                                from_time=items['FromTime'], to_time=items['ToTime'], delete_flg='0')\
                                                .order_by('created_at')[:int(items['Number'])]
                    msg.append(self.main_proc(draws))

        except Exception as e:
            msg.append(super().error_proc(e))

        finally:
            super().finally_proc(''.join(msg))

    def main_proc(self, draws):
        msg = []
        for draw in draws:
            '''ログイン処理'''
            msg.append(super().loginProc(draw.card_id.card_id, draw.card_id.password))
            msg.append(self.cancelApp())

            '''抽選テーブルを論理削除する'''
            draw.delete_flg = '1'
            draw.save()

        return ''.join(msg)

    def cancel_on_line(self, **kwargs):
        try:
            msg = ""
            draws = Draw.objects.filter(card_id__user=kwargs.get('user_id'), year=kwargs.get('year'), month=kwargs.get('month'),\
                                        day=kwargs.get('day'), from_time=kwargs.get('from_time'), to_time=kwargs.get('to_time'), delete_flg='0') \
                        .order_by('created_at')[:int(kwargs.get('cancel_num'))]
            msg += self.main_proc(draws)

        except Exception as e:
            msg += super().error_proc(e)

        finally:
            super().finally_proc(msg)

    def cancelApp(self):
        # キャンセル
        self.driver.find_element_by_id('goLotStatusList').click()
        web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
        num = len(web_elements)
        msg = ""
        if num > 0:
            self.doCancel(num)
            web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
            num = len(web_elements)
            msg += self.doCancel(num)
        self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()
        return msg

    def doCancel(self, num):
        msg = []
        for i in range(num):
            try:
                if self.driver.find_elements_by_id('clsnamem')[i].text.find('テニス') != -1:
                    try:
                        self.driver.find_elements_by_id('goLotConfirm')[i].click()
                    except Exception:
                        continue
                    msg.append("\n" + self.driver.find_element_by_id("bgcdnamem").text \
                        + "\n" + self.driver.find_element_by_id("useymdLabel").text + " " \
                        + self.driver.find_element_by_id("stimeLabel").text \
                        + self.driver.find_element_by_id("etimeLabel").text \
                        + "\n" + self.driver.find_element_by_id("clscdnamem").text)
                    self.driver.find_element_by_id('doCancel').click()
                    self.driver.switch_to_alert().accept()
            except Exception:
                break
        return ''.join(msg)
