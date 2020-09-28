from .business import BudgetCollection
from django.db import IntegrityError
from .models import Budget

class NextMonthBudgetCreator(object):

    @staticmethod
    def copy_current_budget(future_start_date, type):
        currBudget = BudgetCollection.get_current_budget(type)
        #generate next month's budget
        future_budget = []
        for b in currBudget:
            bnew = Budget(
                    start_date = future_start_date,
                    category = b.category,
                    amount = b.amount,
                    freq_month = b.freq_month
                )
            future_budget.append(bnew)
        
        # commit new entries only to db
        added = 0
        for fb in future_budget:
            try:
                fb.save()
                added+=1
            except IntegrityError as e:
                print("budget item already copied to next month's budget plan")
        return added

    