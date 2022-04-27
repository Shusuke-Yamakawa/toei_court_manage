from .command_super import CommandSuper
from ...models import *
from .Lib.utility import Utility

class Command(CommandSuper):
    help = "DrawConfirm Toei"

    """"
    切り替えること
        user_id
        Line通知
        GetListのゴミは消しておく
    """
    def handle(self, *args, **options):

        user_id = Utility.USER_JOIAS

        try:
            msg = []
            lineMsg = ["■抽選当選者通知"]

            draws = Draw.objects.filter(card_id__user=user_id, year=self.year, month=self.month, \
                                        draw_conf_flg='0', delete_flg='0') \
                                        .order_by('created_at')
            for draw in draws:
                # ログイン処理
                msg.append(super().loginProc(draw.card_id.card_id, draw.card_id.password))

                # テニスの抽選のみ確定させる
                self.driver.find_element_by_id('goLotStatusList').click()
                try:
                    web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
                except Exception:
                    self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()
                    continue
                num = len(web_elements)
                if num > 0:
                    lineMsg.append(self.confirm(num, draw))
                    # 2件とも確定している場合
                    web_elements = self.driver.find_element_by_id('lotStatusListItems').find_elements_by_tag_name('tr')
                    num = len(web_elements)
                    lineMsg.append(self.confirm(num, draw))

                self.driver.find_element_by_xpath("//input[@value='ログアウト']").click()

                draw.draw_conf_flg = '1'
                draw.save()

        except Exception as e:
            msg.append(super().error_proc(e))

        finally:
            print(''.join(msg))
            super().finally_proc(''.join(lineMsg))

    def confirm(self, num, draw):
        msg = []
        for i in range(num):
            if self.driver.find_elements_by_id('clsnamem')[i].text.find('テニス') != -1:
                try:
                    self.driver.find_elements_by_id('goLotElectConfirm')[i].click()
                except Exception:
                    continue
                if self.driver.find_element_by_id("bnamem").text:
                    msg.append("\n\n" + self.driver.find_element_by_id("useymdLabel").text + " " \
                        + self.driver.find_element_by_id("stimeLabel").text \
                        + self.driver.find_element_by_id("etimeLabel").text)
                    toei = Toei.objects.get(pk=self.driver.find_element_by_id("userid").text)
                    msg.append("\n" + toei.user_nm_kn)
                    msg.append("\n" + self.driver.find_element_by_id("bnamem").text)
                    msg.append("\n" + self.driver.find_element_by_id("clsnamem").text)
                    get_court = GetCourt(card_id=Toei(draw.card_id.card_id), year=self.year, month=self.month, day=draw.day, \
                                from_time=draw.from_time, to_time=draw.to_time, court=draw.court)
                    get_court.save()
                self.driver.find_element_by_id('doOnceLockFix').click()
        else:
            return ''.join(msg)