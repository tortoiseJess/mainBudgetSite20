from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib import messages

import datetime as dt
from .budget_business import BudgetCollection, NextMonthBudgetCreator
from .utilities import get_next_month
from .models import Budget
from .forms import BudgetForm


class BudgetListView(ListView):
    model = Budget
    template_name = "budget/budget_base_list.html"
    ordering = ['-start_date', 'category__name']
    budget_type = 0

    def get_context_data(self, **kwargs):
        ctx = super(BudgetListView, self).get_context_data(**kwargs)
        ctx['fields'] = ['category', 'monthly_amount', 'start_date', 'freq_month' ]
        
        if 'year' in self.kwargs:
            start_date = "{}-{}".format(self.kwargs['year'],self.kwargs['month'])
            ctx['allow_copy'] = False
            if dt.datetime.strptime(start_date+"-1", "%Y-%m-%d").date() > dt.date.today():
                ctx['allow_create'] = True
        else:
            start_date = dt.datetime.now().date().strftime('%Y-%m')
            ctx['allow_copy'] = True
        ctx['start_date'] = start_date
        ctx['budget_type'] = self.budget_type
        return ctx

    def get_queryset(self):
        qs = BudgetCollection.get_current_budget(self.budget_type)
        if 'year' in self.kwargs and 'month' in self.kwargs:
            y = self.kwargs['year']
            m = self.kwargs['month']
            start_date = dt.date(int(y), int(m), 1)
            qs = Budget.objects.filter(category__type=self.budget_type)\
                                .filter(start_date=start_date)
        return qs

def copyBudgetForm(request, type):
    # if request.method == 'POST':
    nextMonth = get_next_month().month
    currYear =get_next_month().year
    future_start_date = get_next_month()
    added = NextMonthBudgetCreator.copy_current_budget(future_start_date,type)
    messages.info(request, "{} number of budget items were copied".format(added))
    if type==0:
        return redirect('bunnySpend5:budget_list', year=currYear, month=nextMonth)
    #or HttpRedirectResponse(reverse('bunnySpend5:budget_list', args=( currYear, nextMonth)))
    else:
        return redirect('bunnySpend5:budget_income_list', year=currYear, month=nextMonth)
    
class BudgetCreateView(CreateView):
    budget_type =1
    form_class = BudgetForm
    template_name = 'budget/budget_create.html'

    def get_form_kwargs(self):
        kwargs = super(BudgetCreateView, self).get_form_kwargs()
        kwargs.update({'budget_type': self.budget_type, 'min_start_date':get_next_month()})
        return kwargs

    def get_success_url(self):
        if self.budget_type== 0:
            return reverse_lazy('bunnySpend5:budget_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
        else:
            return reverse_lazy('bunnySpend5:budget_income_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
    def get_context_data(self, **kwargs):
        ctx = super(BudgetCreateView, self).get_context_data(**kwargs)
        ctx['budget_type'] = self.budget_type
        return ctx 

    #TODO initial field not showing, got overridden possibily
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.initial['start_date'] = dt.datetime.strftime(\
                get_next_month(prev=False), '%Y-%m-%d')
        return form

class BudgetUpdateView(UpdateView):
    # budget_type =0
    model = Budget  

    form_class = BudgetForm
                
    template_name = "budget/budget_edit.html"

    # pass request args or other data as kwargs to BudgetForm creation
    def get_form_kwargs(self):
        kwargs = super(BudgetUpdateView, self).get_form_kwargs()
        kwargs.update({'budget_type': self.kwargs['budget_type'], 'min_start_date':get_next_month()})
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(BudgetUpdateView, self).get_context_data(**kwargs)
        ctx['budget_type'] = self.kwargs['budget_type']
        return ctx 

    def get_success_url(self):
        if self.kwargs['budget_type'] == 0:
            return reverse_lazy('bunnySpend5:budget_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
        else:
            return reverse_lazy('bunnySpend5:budget_income_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
            

class BudgetDeleteView(DeleteView):
    # success_url = reverse_lazy('bunnySpend5:budget_list',
    #                     kwargs={'year': get_next_month().year, \
    #                               'month': get_next_month().month}) 
    budget_type = 0
    template_name = "budget/budget_delete.html"
    model = Budget

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            self.object = self.get_object()
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(BudgetDeleteView, self).post(request, *args, **kwargs)
            
    def get_success_url(self):
        if self.budget_type == 0:
            return reverse_lazy('bunnySpend5:budget_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
        else:
            return reverse_lazy('bunnySpend5:budget_income_list',
                        kwargs={'year': get_next_month().year, \
                                  'month': get_next_month().month}) 
            
    