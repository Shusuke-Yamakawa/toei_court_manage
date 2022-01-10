from django import forms
from django.core.mail import EmailMessage

from .models import *


class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=30)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=30)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'form-control col-9'
        self.fields['name'].widget.attrs['placeholder'] = 'お名前をここに入力してください。'

        self.fields['email'].widget.attrs['class'] = 'form-control col-11'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスをここに入力してください。'

        self.fields['title'].widget.attrs['class'] = 'form-control col-11'
        self.fields['title'].widget.attrs['placeholder'] = 'タイトルをここに入力してください。'

        self.fields['message'].widget.attrs['class'] = 'form-control col-12'
        self.fields['message'].widget.attrs['placeholder'] = 'メッセージをここに入力してください。'

    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        subject = 'お問い合わせ {}'.format(title)
        message = '送信者名: {0}\nメールアドレス: {1}\nメッセージ:\n{2}'.format(name, email, message)
        from_email = 'leo10blue18@gmail.com'
        to_list = [
            email
        ]
        cc_list = [
            'leo10blue18@gmail.com'
        ]

        message = EmailMessage(subject=subject, body=message, from_email=from_email, to=to_list, cc=cc_list)
        message.send()

class ToeiCreateForm(forms.ModelForm):
    class Meta:
        model = Toei
        fields = ('card_id', 'password', 'user_nm_kj', 'user_nm_kn', 'give_nm', 'expire_date', 'available_flg','share_team','note',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['user_nm_kj'].required = False
        self.fields['expire_date'].required = False
        self.fields['share_team'].required = False
        self.fields['note'].required = False

class GetCreateForm(forms.ModelForm):
    class Meta:
        model = GetCourt
        fields = ('year', 'month', 'day', 'from_time', 'to_time', 'court', 'card_id', 'use_flg',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ToeiSearchForm(forms.Form):
    user_nm_kn = forms.CharField(
        initial='',
        label='名義(カナ)',
        required = False,
    )
    available_flg = forms.ChoiceField(
        initial='',
        label='有効',
        choices=(
            ('', ''),
            ('1', '有効'),
            ('0', '無効')
        ),
        required=False,
        widget=forms.widgets.Select
    )