from .get_time_by_court import GetTimeByCourt

# コート、月別に時間帯を取得するの基底クラス
class GetTimeNightNot(GetTimeByCourt):

    @classmethod
    def get_time(cls, cnt, month):
        time_list = []
        if cnt == 0 or cnt == 1:
            time_list = super().get_time_common(cnt)
        elif cnt == 2 and month in [11, 12, 1, 2]:
            time_list = [13, 16]
        elif cnt == 2 and month not in [11, 12, 1, 2]:
            time_list = [13, 15]
        elif cnt == 3 and month in [5, 8]:
            time_list = [15, 18]
        elif cnt == 3 and month not in [5, 8]:
            time_list = [15, 17]
        elif cnt == 4:
            time_list = [17, 19]
        return time_list