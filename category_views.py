
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from .models import Category
from .forms import CategoryForm



class CategoryListView(ListView):
    model = Category
    template_name = 'category/category_base_list.html'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        ctx = super(CategoryListView, self).get_context_data(**kwargs)
        ctx['fields'] = ['name', 'accumulative', 'type' ]
        return ctx 

class CategoryCreateView(CreateView):
    form_class = CategoryForm
    template_name = 'category/category_create.html'
    success_url = reverse_lazy('bunnySpend5:category_list')

    def get_context_data(self, **kwargs):
        ctx = super(CategoryCreateView, self).get_context_data(**kwargs)
        return ctx 