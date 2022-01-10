from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import redirect
from django.views import generic
from toei.management.commands.Lib.utility import Utility
from toei.management.commands.draw_cancel import Command as draw_cancel
from toei.management.commands.draw_input import Command as draw_input
from toei.models import Draw

class DrawListView(LoginRequiredMixin, generic.ListView):
    model = Draw
    template_name = 'draw_list.html'
    # paginate_by = 10 #モデル件数を使用しない形でのページ処理を研究しておく
    year, month = Utility.get_next_year_month()

    def get_context_data(self, **kwargs):

        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT a.year, a.month, a.day, a.from_time, a.to_time, a.court, count(*) *2 as count,
                   b.odds, cast(count(*) *2 as float)/b.apply_court * b.empty_court as chance
            FROM draw a INNER JOIN odds_court b
                ON a.year = b.year AND a.month = b.month AND a.day = b.day
                AND a.from_time = b.from_time AND a.court = b.court
            WHERE a.year = %s AND a.month = %s And a.delete_flg = '0'
                AND a.card_id in (select card_id from toei where user_id = %s)
            GROUP BY a.year, a.month, a.day, a.from_time, a.to_time, a.court,
                     b.odds, b.apply_court, b.empty_court
            ORDER BY a.day, a.from_time;
            """
            ,[self.year, self.month, self.request.user.id])
        draws = Utility.dictfetchall(cursor)
        context = super().get_context_data(**kwargs)
        context["draw_list"] = draws
        context["draw_list_count"] = draws.__len__()
        return context

    def post(self, request):

        days = self.request.POST.getlist('day', None)
        from_times = self.request.POST.getlist('from_time', None)
        to_times = self.request.POST.getlist('to_time', None)
        courts = self.request.POST.getlist('court', None)
        # キャンセルボタンがクリックされた場合の処理
        cancel_nums = request.POST.getlist('cancel_num')
        for i, cancel_num in enumerate(cancel_nums):
            if cancel_num and int(cancel_num) > 0:
                draw_cancel().cancel_on_line(year=self.year, month=self.month, day=days[i], from_time=from_times[i], \
                                             to_time=to_times[i], cancel_num=cancel_num, user_id=self.request.user.id)
        add_nums = request.POST.getlist('add_num')
        for i, add_num in enumerate(add_nums):
            if add_num and int(add_num) > 0:
                draw_input().input_on_line(year=self.year, month=self.month, Day=days[i], FromTime=from_times[i], \
                                             ToTime=to_times[i], Court=courts[i], add_num=add_num, user_id=self.request.user.id)

        return redirect('toei:draw_list')  # 一覧ページにリダイレクト