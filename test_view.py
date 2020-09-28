from django.test import RequestFactory, TestCase
from .models import *
import datetime as dt 


class TransactionTestCase(TestCase):
    def setUp(self):
        Category.objects.create(
            name = 'furniture',
            accumulative = True,
            checked=False,
        )
        Category.objects.create(
            name = 'clothes',
            accumulative = True,
        )
        Category.objects.create(
            name = 'salary',
            type = 1,
        )
        Category.objects.create(
            name = 'bonus',
            type = 1,
        )
        Transaction.objects.create(
            transaction_date=dt.date(2019,2,13), 
            amount=2600.0,
            description='test1',
            category_id='furniture',
            am_months=36)
        Transaction.objects.create(
            transaction_date=dt.date(2019,4,5), 
            amount=520.0,
            description='test2',
            category_id='furniture',
            am_months=12)
        Transaction.objects.create(
            transaction_date=dt.date(2019,6,23), 
            amount=800.0,
            description='test3',
            category_id='furniture',
            am_months=18)
        Transaction.objects.create(
            transaction_date=dt.date(2019,2,13), 
            amount=200.0,
            description='test4',
            category_id='clothes',
            am_months=24)
        Budget.objects.create(
            category_id = 'furniture',
            amount = 1000,
            start_date = dt.date(2020,6,24),
            freq_month = 0.25
        )
        Budget.objects.create(
            category_id = 'clothes',
            amount = 200,
            start_date = dt.date(2020,6,24),
            freq_month = 0.5
        )
        Budget.objects.create(
            category_id = 'salary',
            amount = 20000,
            start_date = dt.date(2020,6,24),
            freq_month = 0.5
        )
    
    def test_context_data_0(self):
        response = self.client.get('/bunnySpend5/budget/spending/latest')
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 2)

    def test_context_data_1(self):
        response = self.client.get('/bunnySpend5/budget/income/latest')
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)

