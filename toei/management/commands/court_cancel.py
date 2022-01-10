import re
from selenium.common.exceptions import NoSuchElementException
from .command_super import CommandSuper
from ...models import GetCourt


class Command(CommandSuper):
    help = "CourtCancel Toei"

    """"
    切り替えること
      Line通知
    """
    # def handle(self, *args, **options):

    #     # CSVファイルパス
    #     csv_file = settings.CSV_FILE_CANCEL
    #
    #     try:
    #         msg = ""
    #
    #         with open(csv_file, encoding="utf_8") as f:
    #             reader = csv.reader(f)  # readerオブジェクトを作成
    #             header = next(reader)  # 最初の一行をヘッダーとして取得
    #
    #             # 行ごとのリストを処理する
    #             for itemInfo in reader:
    #                 # ディクショナリ化（タプルリスト化後に変換）
    #                 items = dict([(header[x], itemInfo[x]) for x in range(len(header))])
    #                 next_year_month = DrawUtility.get_next_year_month()
    #                 year = next_year_month[0]
    #                 month = next_year_month[1]
    #                 # ユーザーごとに切り替えられるようにする
    #                 draws = Draw.objects.filter(card_id__user='1', year=year, month=month, day=items['Day'], \
    #                                             from_time=items['FromTime'], to_time=items['ToTime'], delete_flg='0')\
    #                                             .order_by('created_at')[:int(items['Number'])]
    #                 for draw in draws:
    #
    #                     # ログイン処理
    #                     msg += DrawUtility.loginProc(self.driver, draw.card_id.card_id, draw.card_id.password)
    #                     msg += self.cancelApp()
    #
    #                     # 抽選テーブルを論理削除する
    #                     draw.delete_flg = '1'
    #                     draw.save()
    #
    #     except Exception as e:
    #         tb = sys.exc_info()[2]
    #         print("エラーメッセージ:{0}".format(e.with_traceback(tb)))
    #         msg += "\n------------------------"
    #         msg += "\n予期せぬエラー発生"
    #
    #     finally:
    #         print(msg)
    #         # LINEに結果を通知する
    #         # QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva 自分だけ
    #         # YG1od8JZaSGqMgBu8dV9wHgBb5kGBBJhPqHBLWToEep JSC
    #         line_notify_token = 'QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva'
    #         line_notify_api = 'https://notify-api.line.me/api/notify'
    #         payload = {'message': msg}
    #         headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
    #         line_notify = requests.post(line_notify_api, data=payload, headers=headers)
    #
    #         # self.driver.close()
    #         # self.driver.quit()
    #
    # def cancelApp(self):
    #     msg = ""
    #     # キャンセル
    #     self.driver.find_element_by_id('goLotStatusList').click()
    #     web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
    #     num = len(web_elements)
    #     if num > 0:
    #         self.doCancel(num)
    #         web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
    #         num = len(web_elements)
    #         msg += self.doCancel(num)
    #     self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()
    #     return msg
    #
    # def doCancel(self, num):
    #     msg = ""
    #     for i in range(num):
    #         try:
    #             if self.driver.find_elements_by_id('clsnamem')[i].text.find('テニス') != -1:
    #                 try:
    #                     self.driver.find_elements_by_id('goLotConfirm')[i].click()
    #                 except Exception:
    #                     continue
    #                 msg += "\n" + self.driver.find_element_by_id("bgcdnamem").text
    #                 msg += "\n" + self.driver.find_element_by_id("useymdLabel").text + " " \
    #                     + self.driver.find_element_by_id("stimeLabel").text \
    #                     + self.driver.find_element_by_id("etimeLabel").text
    #                 msg += "\n" + self.driver.find_element_by_id("clscdnamem").text
    #                 self.driver.find_element_by_id('doCancel').click()
    #                 self.driver.switch_to_alert().accept()
    #         except Exception:
    #             break
    #     return msg

    def cancel_from_online(self, get_court):
        try:
            msg = ""
            # ログイン
            msg += super().loginProc(get_court.card_id.card_id, get_court.card_id.password)
            self.driver.find_element_by_id('goRsvStatusList').click()
            # キャンセル
            msg += self.do_cancel(get_court)
            # 次のページ
            while True:
                try:
                    self.driver.find_element_by_id('goNextPager').click()
                    msg += self.do_cancel(get_court)
                except NoSuchElementException:
                    # 次のページが押せなくなったらループから抜ける
                    break
            get_court.delete()

        except Exception as e:
            msg += (super().error_proc(e))

        finally:
            super().finally_proc(msg)

    def do_cancel(self, get_court):
        web_elements = self.driver.find_elements_by_id('doSelect')
        num = len(web_elements)
        msg = ""
        for i in range(num):
            try:
                if self.driver.find_elements_by_id('ppsname')[i].text != 'テニス（人工芝）':
                    continue
                date = self.driver.find_elements_by_id('ymdLabel')[i].text
                from_time = self.driver.find_elements_by_id('stimeLabel')[i].text
                court_nm = self.driver.find_elements_by_id('bnamem')[i].text
                # DB格納値に変換し、キャンセル対象と突き合わせ
                month = re.match(r'.*年(\d+)月.*', date).group(1)
                day = re.match(r'.*月(\d+)日.*', date).group(1)
                from_time_db = re.match(r'(\d+)', from_time).group(1)

                if get_court.month == int(month) and get_court.day == int(day) \
                        and get_court.from_time == int(from_time_db):
                    self.driver.find_elements_by_id('doSelect')[i].click()
                    self.driver.find_element_by_id('doDelete').click()
                    self.driver.switch_to_alert().accept()
                    msg += "\n" + date + " " \
                           + from_time + " " \
                           + court_nm
            except Exception as e:
                continue
        return msg
