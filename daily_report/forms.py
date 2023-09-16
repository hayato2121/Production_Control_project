from django import forms

from .models import Report



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


class ReportEndForm(forms.ModelForm):
    memo = forms.CharField(label='引き継ぎ', widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    sets = forms.IntegerField(label='セット数')
    quantity = forms.IntegerField(label='数量', disabled=True)

    class Meta:
        model = Report
        fields = ['product','business','user','lot_number','quantity',
                  'sets','bad_product','memo']

    #詳細ページからデータを引き出し、初期値に登録する。
    def __init__(self, *args, **kwargs):
        super(ReportEndForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            initial_data ={
                'product': kwargs['instance'].product,
                'business': kwargs['instance'].business,
                'user': kwargs['instance'].user,
                'lot_number': kwargs['instance'].lot_number,
                'quantity': kwargs['instance'].product.quantity
            }
            self.initial.update(initial_data)



    
    
        
