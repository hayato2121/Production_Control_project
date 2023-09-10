from django import forms

from .models import Products,Business,Report

class ReportTaskForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Products.objects,
        label='製品名', 
        required=True,)
    Business = forms.ModelChoiceField(queryset=Business.objects,
        label='業務内容', 
        required=True,)
    
    class Meta:
        model = Report
        fields = ['product', 'Business']

    
