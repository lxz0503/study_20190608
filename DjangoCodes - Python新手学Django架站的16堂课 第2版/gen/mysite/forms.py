#coding: utf-8
import os
from django import forms

class GenForm(forms.Form):
    msg = forms.CharField(label='信息', widget=forms.Textarea)
    font_size = forms.IntegerField(label='文字尺寸(12-80)', min_value=12, max_value=80)
    x = forms.IntegerField(label='X(0-50)', min_value=0, max_value=50)
    y = forms.IntegerField(label='Y(0-100)', min_value=0, max_value=100)
    def __init__(self, backfiles, *args, **kwargs):
        super(GenForm, self).__init__(*args, **kwargs)
        self.fields['backfile'] = forms.ChoiceField(
                choices=[(os.path.basename(bf), os.path.basename(bf)) for bf in backfiles]
        )

class CustomForm(forms.Form):
    msg = forms.CharField(label='信息', widget=forms.Textarea)
    font_size = forms.IntegerField(label='文字尺寸(12-120)', min_value=12, max_value=120)
    x = forms.IntegerField(label='X(0-400)', min_value=0, max_value=400)
    y = forms.IntegerField(label='Y(0-600)', min_value=0, max_value=600)

class UploadForm(forms.Form):
    file = forms.FileField()