import requests
import logging

from .command_super import CommandSuper
from ...models import Toei
from .Lib.utility import Utility

logger = logging.getLogger(__name__)

class Command(CommandSuper):
    help = "CourtRecover Toei"

    """"
    切り替えること
      Line通知
      いずれ定期バッチに変更する
    """
    def handle(self, *args, **options):

        self.recover_from_online("")

    def recover_from_online(self, user_id):
        try:
            no_change_msg = ""
            recover_msg = ""
            del_chk_msg = ""

            # ログイン
            if user_id:
                toeis = Toei.objects.filter(user=user_id, available_flg='0', delete_flg='0').order_by('-updated_at')
            else:
                toeis = Toei.objects.filter(available_flg='0', delete_flg='0').order_by('-updated_at')
            for toei in toeis:
                del_chk_msg += super().loginProc(toei.card_id, toei.password)
                if del_chk_msg.find('論理削除済') != -1:
                    continue
                # 期限切れチェック
                msg = super().warnExpired(toei, True)
                if msg.find("【回復】") != -1:
                    recover_msg += msg
                else:
                    no_change_msg += msg
                self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()

        except Exception as e:
            recover_msg += super().error_proc(e)

        finally:
            if del_chk_msg.find('論理削除済') != -1:
                logger.info(del_chk_msg)
            logger.info(recover_msg)
            logger.info(no_change_msg)
            # LINEに結果を通知する
            # QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva 自分だけ
            # YG1od8JZaSGqMgBu8dV9wHgBb5kGBBJhPqHBLWToEep JSC
            if not recover_msg:
                recover_msg += "回復した名義なし"
            line_notify_token = 'QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva'
            line_notify_api = 'https://notify-api.line.me/api/notify'
            payload = {'message': recover_msg}
            headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
            line_notify = requests.post(line_notify_api, data=payload, headers=headers)
            self.driver.close()
            self.driver.quit()