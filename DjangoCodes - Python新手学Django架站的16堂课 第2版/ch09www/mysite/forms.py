#_*_ encoding: utf-8 *_*
from django import forms
from . import models


class ContactForm(forms.Form):
    CITY = [
        ['SH', 'Shanghai'],
        ['GZ', 'Guangzhou'],
        ['NJ', 'Nanjing'],
        ['HZ', 'Hangzhou'],
        ['WH', 'Wuhan'],
        ['NA', 'Others'],
]
user_name = forms.CharField(label='您的姓名', max_length=50, initial='李大仁')
    user_city = forms.ChoiceField(label='居住城市', choices=CITY)
    user_school = forms.BooleanField(label='是否在学', required=False)
    user_email = forms.EmailField(label='电子邮件')
    user_message = forms.CharField(label='您的意见', widget=forms.Textarea)


class PostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ['mood', 'nickname', 'message', 'del_pass']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['mood'].label = '现在心情'
        self.fields['nickname'].label = '你的昵称'
        self.fields['message'].label = '心情留言'
        self.fields['del_pass'].label = '设置密码'


class LoginForm(forms.Form):
    username = forms.CharField(label='姓名', max_length=10)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())


class DateInput(forms.DateInput):
    input_type = 'date'

class DiaryForm(forms.ModelForm):

    class Meta:
        model = models.Diary
        fields = ['budget', 'weight', 'note', 'ddate']
        widgets = {
            'ddate': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DiaryForm, self).__init__(*args, **kwargs)
        self.fields['budget'].label = '今日花费(元)'
        self.fields['weight'].label = '今日体重(KG)'
        self.fields['note'].label = '心情留言'
        self.fields['ddate'].label = '日期'