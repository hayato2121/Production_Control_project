from django import forms

from .models import Report
from .models import Business



class ReportStartForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('product', 'business')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportStartForm, self).__init__(*args, **kwargs)
        
        if self.user and self.user.department:
            # ユーザーの部署と紐づく業務内容のみを選択肢として表示
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)


    #userフィールドに自動でリクエストユーザーをする。
    def save(self, commit=True):
        report = super(ReportStartForm, self).save(commit=False)
        if self.user:
            report.user = self.user
        if commit:
            report.save()
        return report


class ReportEndForm(forms.ModelForm):
    memo = forms.CharField(label='引き継ぎ',initial='なし',widget=forms.TextInput(attrs={'style': 'width: 200px; height: 100px;'}))
    sets = forms.IntegerField(label='セット数')
    bad_product = forms.IntegerField(label='不良数')
    quantity = forms.IntegerField(label='数量', disabled=True)
    
    class Meta:
        model = Report
        fields = ['product','business','user','lot_number','quantity',
                  'sets','bad_product','memo']

    #初期値。
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReportEndForm, self).__init__(*args, **kwargs)

        
        # ユーザーの部署と紐づく業務内容のみを選択肢として表示
        if self.user and self.user.department:
            self.fields['business'].queryset = Business.objects.filter(department=self.user.department)
        
        #詳細データからデータを引き出し初期値に登録
        if 'instance' in kwargs and kwargs['instance']:
            initial_data ={
                'product': kwargs['instance'].product,
                'business': kwargs['instance'].business,
                'user': kwargs['instance'].user,
                'lot_number': kwargs['instance'].lot_number,
                'quantity': kwargs['instance'].product.quantity
            }
            self.initial.update(initial_data)


        #初期値に設定したデータを編集できないようにする
        for field_name in [ 'product', 'business', 'user','lot_number']:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'



    
    
        
