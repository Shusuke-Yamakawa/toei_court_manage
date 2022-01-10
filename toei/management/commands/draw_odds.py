import calendar
import datetime

from .Lib.day_judge_holiday import DayJudgeHoliday
from .Lib.get_time_night_avail import GetTimeNightAvail
from .Lib.get_time_night_not import GetTimeNightNot
from .command_super import CommandSuper
from ...models import OddsCourt


class Command(CommandSuper):
    help = "DrawOdds Toei"
    def handle(self, *args, **options):

        try:
            msg = []
            super().loginProc('86329044', '19870513')

            for day in self._handle_dates(self.year, self.month, 1):
                if  DayJudgeHoliday.target_day(datetime.date(self.year, self.month, day)):
                    day = str(day)
                    msg.append("\n\n" + "■" + day + "日")
                    msg.append("\n" + "---府中の森---")
                    msg.append(self.drawInfo(day, "0"))
                    msg.append("\n" + "---小金井公園---")
                    msg.append(self.drawInfo(day, "1"))
                    msg.append("\n" + "---野川公園---")
                    msg.append(self.drawInfo(day, "2"))
                    msg.append("\n" + "---井の頭公園---")
                    msg.append(self.drawInfo(day, "3"))


        except Exception as e:
            msg.append(super().error_proc(e))

        finally:
            super().finally_proc(''.join(msg))

    def drawInfo(self, day, setCourt):
        self.driver.find_element_by_id('goLotSerach').click()
        self.driver.find_element_by_xpath("//input[@value='130']").click()
        self.driver.find_element_by_id('goFavLotList').click()
        # お気に入りの先頭が0
        # 0が府中の森、1が小金井公園、2が野川公園、3が井の頭公園とする
        self.driver.find_element_by_xpath("//input[@type='radio' and @value='" + setCourt + "']").click()
        self.driver.find_element_by_xpath("//input[@value='抽選の申し込みをおこなう']").click()
        self.driver.find_element_by_link_text(day).click()
        emptyCnt = self.driver.find_elements_by_id('emptyCnt')
        applyCnt = self.driver.find_elements_by_id('appCnt')
        msg = []
        loopCnt = 0
        for (empty, apply) in zip(emptyCnt, applyCnt):
            msg.append("\n" + apply.text + "/" + empty.text + "  ")
            calcInfo = round(float(apply.text) / float(empty.text), 2)
            msg.append(str(calcInfo))
            time_list = self.get_time(loopCnt, self.month, setCourt)
            odds_court = OddsCourt.objects.filter(year=self.year, month=self.month, day=day, from_time=time_list[0], \
                                                  to_time=time_list[1], court=setCourt).first()
            if odds_court:
                odds_court.odds = calcInfo
                odds_court.empty_court = int(empty.text)
                odds_court.apply_court = int(apply.text)
                odds_court.save()
            else:
                odds_court_new = OddsCourt(year=self.year, month=self.month, day=day, from_time=time_list[0], \
                                     to_time=time_list[1], court=setCourt, odds=calcInfo, \
                                      empty_court=int(empty.text), apply_court=int(apply.text))
                odds_court_new.save()
            loopCnt += 1
        self.driver.find_element_by_xpath("//input[@value='マイページへ']").click()
        return ''.join(msg)

    @staticmethod
    def _handle_dates(year, month, day):
        mr = calendar.monthrange(year, month)
        return range(day, mr[1] + 1)

    def get_time(self, loopCnt, month, court):
        if court == '0':
            getTime = GetTimeNightAvail
        else:
            getTime = GetTimeNightNot

        return getTime.get_time(loopCnt, month)