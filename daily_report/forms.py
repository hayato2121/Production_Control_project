from django import forms

from .models import Report

from datetime import datetime

class ReportStartForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('product', 'business')

    def __init__(self,*args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportStartForm, self).__init__(*args, **kwargs)

    #userフィールドに自動でリクエストユーザーをする。
    def save(self, commit=True):
        report = super(ReportStartForm, self).save(commit=False)
        if self.user:
            report.user = self.user
        if commit:
            report.save()
        report.save()
        return report


class RepoertEndForm(forms.ModelForm):
    
    class Meta:
        models = Report

    
    
        
