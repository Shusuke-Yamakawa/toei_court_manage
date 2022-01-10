from abc import *

# コート、月別に時間帯を取得するの基底クラス
class GetTimeByCourt(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_time(cls, cnt, month):
        pass

    @classmethod
    def get_time_common(cls, cnt):
        time_list = []
        if cnt == 0:
            time_list = [9, 11]
        elif cnt == 1:
            time_list = [11, 13]
        return time_list