import sys
from abc import abstractmethod
import time
import logging
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from toei.models import Toei

from .Lib.utility import Utility
logger = logging.getLogger(__name__)

class CommandSuper(BaseCommand):
    help = "Super Toei"

    def __init__(self):
        self.year, self.month = Utility.get_next_year_month()

        if settings.HEADLESS == 1:
            options = Options()
            # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1280,1024')
            # ChromeのWebDriverオブジェクトを作成する。
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(1)

    @abstractmethod
    def handle(self, *args, **options):
        pass

    def loginProc(self, id, passwd):
        # self.driver.get("https://yoyaku.sports.metro.tokyo.jp/user/view/user/homeIndex.html")
        self.driver.get("https://yoyaku.sports.metro.tokyo.lg.jp/user/view/user/homeIndex.html")
        self.driver.find_element_by_id('login').click()
        logger.info('ログイン処理開始 ID/PW %s %s', id, passwd)
        user_id = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'userid')))
        user_id.send_keys(id)
        self.driver.find_element_by_id('passwd').send_keys(passwd)
        time.sleep(3)
        self.driver.find_element_by_id('login').click()
        toei = Toei.objects.get(pk=id)
        # self.driver.save_screenshot(settings.CAPTURE_DIRS + id + "_loginAfter.png")
        try:
           return "\n\n" + toei.user_nm_kn
        except Exception:
            web_element = self.driver.find_element_by_xpath("//*[@id='allMessages']/li")
            try:
                if web_element.text.find('登録番号、またはパスワードが誤っています。') != -1:
                    toei.delete_flg = '1'
                    toei.save()
                    return "\n\n" + toei.user_nm_kn + "１年更新なしのため、論理削除済"
            except Exception:
                return "\n\n" + toei.user_nm_kn + "タイムアウト"


    def warnExpired(self, toei, recover):
        '''期限切れ警告'''
        try:
            web_element = self.driver.find_element_by_xpath(
                "//*[@id='childForm']/div/table[1]/tbody/tr[2]/td/div/dl[2]/dd/font/u")
            if web_element.text.find('有効期限が切れます') != -1:
                warnMsg = "\n\n" + toei.user_nm_kn
                warnMsg += " 【期限切れ直前】"
                return warnMsg
            elif web_element.text.find('有効期限が切れている') != -1:
                toei.available_flg = '0'
                toei.save()
                warnMsg = "\n\n" + toei.user_nm_kn
                warnMsg += " 【期限切れ】"
                return warnMsg
            elif web_element.text.find('ペナルティ期間中') != -1:
                logger.warning("\n\n" + toei.user_nm_kn + " 【ペナルティ期間中】")
                return ""
            else:
                return ""
        # 警告メッセージの表示がない場合
        except Exception:
            # 元々警告状態の名義に関しては、回復させる
            if recover:
                toei.available_flg = '1'
                toei.save()
                warnMsg = "\n\n" + toei.user_nm_kn
                warnMsg += " 【回復】"
                return warnMsg
            else:
                return ""

    @staticmethod
    def error_proc(e):
        tb = sys.exc_info()[2]
        error_msg = "エラーメッセージ:{0}".format(e.with_traceback(tb))
        logger.error(error_msg)
        return "\n------------------------\n予期せぬエラー発生\n" + error_msg

    def finally_proc(self, msg):
        logger.info(msg)
        # LINEに結果を通知する
        # QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva 自分だけ
        # YG1od8JZaSGqMgBu8dV9wHgBb5kGBBJhPqHBLWToEep JSC
        line_notify_token = 'QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva'
        line_notify_api = 'https://notify-api.line.me/api/notify'
        payload = {'message': msg}
        headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
        line_notify = requests.post(line_notify_api, data=payload, headers=headers)

        self.driver.close()
        self.driver.quit()