from django import forms

#年と月の選択肢
YEAR_CHOICES = [(year, str(year)) for year in range(2020, 2026)]  # 2020年から2030年までの範囲を選択肢にする例

MONTH_CHOICES = [
    (1, '1月'), (2, '2月'), (3, '3月'), (4, '4月'),
    (5, '5月'), (6, '6月'), (7, '7月'), (8, '8月'),
    (9, '9月'), (10, '10月'), (11, '11月'), (12, '12月')
]

#グラフに渡す年と月を入力するフォーム
class GraphYearMonthForm(forms.Form):
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='年')
    month = forms.ChoiceField(choices=MONTH_CHOICES, label='月')