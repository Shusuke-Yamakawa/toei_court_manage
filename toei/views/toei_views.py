from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.db import connection, transaction
from django.urls import reverse_lazy
from django.views import generic
from toei.forms import *
from toei.management.commands.card_recover import Command as card_recover
from toei.models import Toei

class ToeiListView(LoginRequiredMixin, generic.ListView):
    model = Toei
    template_name = 'toei_list.html'
    paginate_by = 10

    def post(self, request, *args, **kwargs):

        # 検索ボタンがクリックされた場合の処理
        form_value = [
            self.request.POST.get('user_nm_kn', None),
            self.request.POST.get('available_flg', None),
        ]
        request.session['form_value'] = form_value
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        # 有効化ボタンを押下時は有効期限回復処理を起動させる
        if 'recover' in request.POST:
            card_recover().recover_from_online(self.request.user)
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        # sessionに値がある場合、その値でクエリ発行する。
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            user_nm_kn = form_value[0]
            available_flg = form_value[1]
            # 検索条件
            condition_nm = Q()
            condition_available = Q()
            if len(user_nm_kn) != 0 and user_nm_kn[0]:
                condition_nm = Q(user_nm_kn__icontains=user_nm_kn)
            if len(available_flg) != 0 and available_flg[0]:
                condition_available = Q(available_flg__exact=available_flg)
            return Toei.objects.select_related().filter(user=self.request.user).filter(delete_flg='0').filter(
                condition_nm & condition_available).order_by('-created_at').reverse()
        else:
            return Toei.objects.select_related().filter(user=self.request.user).order_by('-created_at').reverse()

    def get_context_data(self, **kwargs):
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        user_nm_kn = ''
        available_flg = ''
        if 'form_value' in self.request.session:
            user_nm_kn = self.request.session['form_value'][0]
            available_flg = self.request.session['form_value'][1]
        default_data = {'user_nm_kn': user_nm_kn,  # タイトル
                        'available_flg': available_flg,  # 内容
                        }
        context = super().get_context_data(**kwargs)
        context['search_form'] = ToeiSearchForm(initial=default_data) # 検索フォーム
        return context

class ToeiDetailView(LoginRequiredMixin, generic.DetailView):
    model = Toei
    template_name = 'toei_detail.html'

class ToeiCreateView(LoginRequiredMixin, generic.CreateView):
    model = Toei
    template_name = 'toei_create.html'
    form_class = ToeiCreateForm
    success_url = reverse_lazy('toei:toei_list')

    def form_valid(self, form):
        toei = form.save(commit=False)
        toei.user = self.request.user
        toei.save()
        messages.success(self.request, 'カード情報を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "カード情報の登録に失敗しました。")
        return super().form_invalid(form)

class ToeiUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Toei
    template_name = 'toei_update.html'
    form_class = ToeiCreateForm

    def get_success_url(self):
        return reverse_lazy('toei:toei_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, 'カード情報を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "カード情報の更新に失敗しました。")
        return super().form_invalid(form)

class ToeiDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Toei
    template_name = 'toei_delete.html'
    success_url = reverse_lazy('toei:toei_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "カード情報を削除しました。")
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE toei SET delete_flg = '1' WHERE card_id = %s;
            """
            , [str(self.kwargs['pk'])])
        transaction.commit()
        return redirect('toei:toei_list')