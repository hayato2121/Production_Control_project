from django import forms

from .models import Products,Business,Report

class ReportStartForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Products.objects,
        label='製品名', 
        required=True,)
    business = forms.ModelChoiceField(queryset=Business.objects,
        label='業務内容', 
        required=True,)
    
    class Meta:
        model = Report
        fields = ('product', 'business')

class RepoertEndForm(forms.ModelForm):
    
    class Meta:
        models = Report
        exclude = 'product', 'business'
