from django.db import models
import datetime 
from .utilities import *
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum

class Budget(models.Model):
    category = models.ForeignKey('Category', models.DO_NOTHING,
     to_field='name', db_column='category'
     )
    amount = models.FloatField()
    start_date = models.DateField()
    freq_month = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'budget'
        constraints = [
            models.UniqueConstraint(fields=[ 'category', 'start_date'],\
                        name="unique month-category budget")
            ]
    
    def formated_amount(self):
        return format_currency(self.amount)
        
    @staticmethod
    def get_column_names():
        return ['id', 'category_id', 'amount', 'start_date_id', 'freq_month']

class CategoryType(Enum):
    Expense = 0
    Income = 1

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

class Category(models.Model):
    name = models.CharField(unique=True, max_length=30)
    accumulative = models.BooleanField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True, default=True)

    TYPE_CHOICES = [(0, 'Expense'), (1, 'Income')]
    type = models.IntegerField(blank=False, default=0, \
        validators=[MaxValueValidator(1), MinValueValidator(0)]) 
    
    class Meta:
        db_table = 'category'
    
    def __str__(self):
        return '%s' % self.name

class Seed(models.Model):
    category = models.ForeignKey(Category, models.DO_NOTHING,
     to_field='name',db_column='category'
     )
    amount = models.FloatField()
    date = models.DateField()

    class Meta:
        db_table = 'seed'


class Transaction(models.Model):
    transaction_date = models.DateField()
    amount = models.FloatField()
    currency = models.CharField(max_length=3, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, models.DO_NOTHING,\
        to_field='name', db_column='category' ) 
    am_months = models.FloatField(blank=True, null=True)
    checked = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'transaction'
    
    @staticmethod
    def get_column_names():
        return ['id', 'transaction_date', 'amount', 'currency', 
                'description', 'category_id', 'am_months' ]
    
    def get_amor_dates(self):
        """
        @para am_months: (int) number of months
        @param date: (str) entry date
        returns: List [start, end dates] as %Y-%m-%d strings
        """
        sd, ed = '', ''
        entry_date = self.transaction_date # "%Y-%m-%d" #2019-08-07
        delta = datetime.timedelta(self.am_months*(365/12))
        if self.am_months>=0:
            sd = entry_date
            ed = entry_date + delta
        else:
            sd = entry_date + delta
            ed = entry_date
        sd = datetime.datetime.strftime(sd,"%Y-%m-%d" )
        ed = datetime.datetime.strftime(ed,"%Y-%m-%d")
        return [sd,ed]
    
    def compute_daily_amortized_cost(self):
        if self.am_months is None:
            return self.amount
        elif self.am_months > 0 or self.am_months < 0:
            return abs(self.amount / (self.am_months*30))
        else:
            return self.amount

    def formated_amount(self):
        return format_currency(self.amount)
