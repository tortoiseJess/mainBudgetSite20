from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.forms import ModelForm
from django import forms
from .models import Transaction, Category
from django.views.generic.edit import CreateView
from django.views.generic.dates import MonthArchiveView
from django.http import HttpResponseRedirect
from django.views.generic.edit import  DeleteView, UpdateView
from django.views.generic import  TemplateView

from .models import Transaction, Category
from .forms import TransactionForm




def autocomplete_description(request):
    if 'term' in request.GET:
        qs = Transaction.objects.filter(description__icontains=request.GET.get('term'))
        descriptions = set()
        for t in qs:
            descriptions.add(t.description)
        return JsonResponse(list(descriptions), safe=False)
    return render(request, 'auto_transaction.html')


def autocomplete_category(request, category_type):

    if 'term' in request.GET:
        qs = Category.objects\
                .filter(type=category_type)\
                .filter(name__icontains=request.GET.get('term'))
        cats = set()
        for t in qs:
            cats.add(t.name)
        return JsonResponse(sorted(cats), safe=False)
    return render(request, 'auto_transaction.html')


class TransactionByMonth(MonthArchiveView):
    '''monthly view of transactions of type = spending'''
    category_type = 0
    queryset = Transaction.objects.filter(category__type=category_type)
    date_field = "transaction_date"
    model = Transaction
    template_name = "transaction/transaction_month_list.html"
    ordering = ['-pk']
    allow_empty = True 
    allow_future = True


    def get_context_data(self, **kwargs):
        ctx = super(TransactionByMonth, self).get_context_data(**kwargs)
        ctx['fields'] = ['transaction_date', 'category', 'amount',\
            'description','am_months' ]
        return ctx


class TransactionForm2(ModelForm):
    class Meta:
        model = Transaction
        fields = ('transaction_date', 'amount', 'description', \
                  'category','am_months', 'checked' )
        widgets = {
            'transaction_date': forms.DateInput(format="%Y-%m-%d"),
        }

class TransactionCreate2(CreateView):
    '''Embed autocomplete into createView form'''
    form_class = TransactionForm2
    template_name = 'auto_transaction.html'

    def get_success_url(self):
        return reverse_lazy('bunnySpend5:transaction_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # make the 'name' field use a datalist to autocomplete
        form.fields['category'].widget.attrs.update({'list': 'names'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add `names` to the context to populate the datalist
        context['names'] = Category.objects.values_list('name', flat=True)
        return context

class TransactionUpdateView(UpdateView):
    model = Transaction   
    form_class = TransactionForm
    template_name = "transaction/transaction_update.html"

    def get_form_kwargs(self):
        kwargs = super(TransactionUpdateView, self).get_form_kwargs()
        category_type = self.get_category_type()
        kwargs.update({'category_type': category_type, })
        return kwargs

    def get_success_url(self):
        trans_date = Transaction.objects.get(pk=self.kwargs['pk']).transaction_date
        month = trans_date.month
        year = trans_date.year
        return reverse_lazy('bunnySpend5:transaction_month_list', \
                        kwargs={'year': year, 'month': month, \
                        'category_type': self.get_category_type() }) 
                        
    def get_category_type(self):
        obj = Transaction.objects.get(pk=self.kwargs['pk'])
        category_type = obj.category.type
        return category_type
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_type'] = self.get_category_type()
        return context

class TransactionDeleteView(DeleteView):
    template_name = "transaction/transaction_delete.html"
    model = Transaction 

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            self.object = self.get_object()
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(TransactionDeleteView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self.get_category_type() == 0:
            return reverse_lazy('bunnySpend5:transaction_list') 
        else:
            return reverse_lazy('bunnySpend5:transaction_income_list')

    def get_category_type(self):
        obj = Transaction.objects.filter(pk=self.kwargs['pk']).first()
        category_type = obj.category.type
        return category_type

class TransactionSearch(TemplateView):
    template_name = "transaction/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_type = self.kwargs['category_type']
        context['category_all'] = [c.name for c in Category.objects.filter(type=category_type)]\
                                        +['all_above']
        context['category_type'] = category_type
        return context
