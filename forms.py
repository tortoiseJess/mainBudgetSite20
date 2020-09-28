from .models import *
from django.forms import ModelForm, modelformset_factory
from django import forms
from .business import CategoryCollection
from django.urls import reverse 
import datetime


class DateInput(forms.DateInput):
    input_type = 'date' 
    format = '%Y-%m-%d'

class TransactionForm(ModelForm):

    class Meta:
        model = Transaction
        fields = ('transaction_date', 'amount', 'am_months', 'checked',
                'description', 'category' )
        widgets = {
            'transaction_date': forms.DateInput(format="%Y-%m-%d" ), 
            'category': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        self.category_type = kwargs.pop('category_type',0)
        super().__init__(*args, **kwargs)

                 
    def clean(self):
        cleaned_data = super().clean()
        amorMonths = cleaned_data['am_months']
        if amorMonths is None:
            cleaned_data['am_months'] = 0
            

class BudgetForm(ModelForm):
    class Meta:
        model = Budget
        fields = ('start_date', 'amount', \
                  'category','freq_month' )
        widgets = {
            'start_date': forms.DateInput(format="%Y-%m-%d"),
            'category': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        budget_type = kwargs.pop('budget_type',0)
        min_start_date = kwargs.pop('min_start_date')

        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects\
                                                .filter(type=budget_type)\
                                                .order_by('-name')

    def clean(self):
        cleaned_data = super().clean()
        if 'start_date' in cleaned_data:
            syr, smonth, _ = str(cleaned_data['start_date']).split('-')
            syr = int(syr)
            smonth = int(smonth)
            cleaned_data['start_date'] = datetime.date(year=syr, month=smonth, day=1)

class CategoryForm(ModelForm):
    type = forms.TypedChoiceField(choices=[(0, 'Expense'), (1, 'Income')], coerce=int)
    class Meta:
        model = Category
        fields = ('name', 'type', \
                  'accumulative' )

    def clean_name(self):
        lower_case_name= self.cleaned_data['name'].lower()
        return lower_case_name
    
    