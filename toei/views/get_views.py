import datetime
import re
import requests

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from toei.forms import *
from toei.management.commands.Lib.utility import Utility
from toei.management.commands.Lib.write_court_info import WriteCourtInfo
from toei.management.commands.court_cancel import Command as court_cancel
from toei.models import *

class GetListView(LoginRequiredMixin, generic.ListView):
    model = GetCourt
    template_name = 'get_list.html'
    paginate_by = 10

    def get_queryset(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        next_year, next_month = Utility.get_next_year_month()
        get = GetCourt.objects.filter(card_id__user=self.request.user, year__in=[year, next_year],\
                                    month__in=[month, next_month], delete_flg='0')\
                                    .order_by('month', 'day', 'from_time', 'court', 'card_id')
        return get

    def post(self, request):
        print(request.POST)
        if 'del' in request.POST:
            pks = request.POST.getlist('delete')  # <input type="checkbox" name="delete"のnameに対応
            for pk in pks:
                get_court = GetCourt.objects.get(pk=pk)
                if get_court.use_flg == "1":
                    messages.warning(self.request, "使用が確定しています。")
                    return redirect('toei:get_list')
                else:
                   court_cancel().cancel_from_online(get_court)
            messages.success(self.request, "コート取得情報を削除しました。")
        elif 'line' in request.POST:
            pks = request.POST.getlist('delete')
            msg = []
            for pk in pks:
                get_court = GetCourt.objects.get(pk=pk)
                # 日にちとコート名義を取得し、msgに格納⇒ラインに連携する
                msg.append("\n" + str(get_court.day) + "日" + str(get_court.from_time) + "時" + "-" +
                           str(get_court.to_time) + "時" + "\n" + get_court.card_id.user_nm_kn)

            # LINEに結果を通知する
            # QUGBKHPEM8JtPKI1mTMrkw8Cxk6KUBogr2poZhEQeva 自分だけ
            # DU1AtUWOsd0tA8yghyHmMT1I4lqkUQGxncEYNINhLrX TBK
            line_notify_token = 'DU1AtUWOsd0tA8yghyHmMT1I4lqkUQGxncEYNINhLrX'
            line_notify_api = 'https://notify-api.line.me/api/notify'
            payload = {'message': ''.join(msg)}
            headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
            line_notify = requests.post(line_notify_api, data=payload, headers=headers)

            messages.success(self.request, "ラインにコート名義を連携しました。")

        elif 'scc' in request.POST:
            date = request.POST.getlist('date')[0]
            year = datetime.date.today().year
            next_year = year + 1
            if not date:
                messages.warning(self.request, "日付(m/d)を設定してください。")
                return redirect('toei:get_list')
            month = re.match(r'(\d+)/(\d+)', date).group(1)
            day = re.match(r'(\d+)/(\d+)', date).group(2)
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT a.year, a.month, a.day, a.from_time, a.to_time, b.user_nm_kn, count(*) count
                FROM get_court a INNER JOIN toei b ON a.card_id = b.card_id
                WHERE a.year in(%s, %s) AND a.month = %s AND a.day = %s And a.delete_flg = '0' And b.user_id = %s
                GROUP BY a.year, a.month, a.day, a.from_time, a.to_time, b.user_nm_kn
                ORDER BY a.from_time, b.user_nm_kn;
                """
                , [year, next_year, month, day, self.request.user.id])
            get_courts = Utility.dictfetchall(cursor)
            if get_courts.__len__() != 0:
                WriteCourtInfo.write_scc(get_courts)
                # LINEに結果を通知する
                # YG1od8JZaSGqMgBu8dV9wHgBb5kGBBJhPqHBLWToEep JSC
                line_notify_token = 'YG1od8JZaSGqMgBu8dV9wHgBb5kGBBJhPqHBLWToEep'
                line_notify_api = 'https://notify-api.line.me/api/notify'
                payload = {'message': '\nスプレッドシートにコート名義書いたよ'}
                headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
                line_notify = requests.post(line_notify_api, data=payload, headers=headers)
                messages.success(self.request, "スプシにコート名義を書き込みました。")
            else:
                messages.success(self.request, "指定した日付にコートはありません")
        return redirect('toei:get_list')  # 一覧ページにリダイレクト

class GetDetailView(LoginRequiredMixin, generic.DetailView):
    model = GetCourt
    template_name = 'get_detail.html'

class GetCreateView(LoginRequiredMixin, generic.CreateView):
    model = GetCourt
    template_name = 'get_create.html'
    form_class = GetCreateForm
    success_url = reverse_lazy('toei:get_list')

    def form_valid(self, form):
        toei = form.save(commit=False)
        toei.user = self.request.user
        toei.save()
        messages.success(self.request, 'コート取得情報を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "コート取得情報の登録に失敗しました。")
        return super().form_invalid(form)

class GetUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = GetCourt
    template_name = 'get_update.html'
    form_class = GetCreateForm

    def get_success_url(self):
        return reverse_lazy('toei:get_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, 'コート取得情報を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "コート取得情報の更新に失敗しました。")
        return super().form_invalid(form)

class GetDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = GetCourt
    template_name = 'get_delete.html'
    success_url = reverse_lazy('toei:get_list')

    def delete(self, request, *args, **kwargs):
        pk = kwargs['pk']
        court_cancel().cancel_from_online(pk)

        messages.success(self.request, "コート取得情報を削除しました。")
        return super().delete(request, *args, **kwargs)