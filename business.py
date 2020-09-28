from .models import *
from .utilities import dateRange_intersection
import datetime as dt
import pandas as pd
import numpy as np 
from django.core.exceptions import *
from django.db.models import Sum

class BudgetCollection():

    @staticmethod
    def get_current_budget(type):
        """
        current budget = budget entries with start_date = current month
        :return: querySet of budgets
        """
        t = dt.datetime.today().date()
        budget = Budget.objects\
                    .filter(start_date__year=t.year,\
                        start_date__month=t.month)\
                    .filter(category__type=type)
        return budget

class CategoryCollection():

    @staticmethod
    def get_current_categories(type):
        """
        :return: List<String> Name of current categories
        """
        budget_objects = BudgetCollection.get_current_budget(type)
        return [b.category.name for b in budget_objects]
    
    @staticmethod
    def get_accum_categories_by_type(type=0):
        qobj = Category.objects.filter(accumulative=True, type=type)
        return [c.name for c in qobj]
    
    @staticmethod
    def get_categories_by_type(type=0):
        qobj = Category.objects.filter(type=type)
        return [c.name for c in qobj]


class Transaction_Amortizer():
    """computes the amortization column from price, amor_dates"""

    def __init__(self, filter=None, category_type=0):
        """
        fiterDict={date_range: list [datetime.date objects, %Y-%m-%d], amortization start/end dates
        category: name}
        """
        self._filter = filter
        df = pd.DataFrame(Transaction.objects.filter(category__type=category_type).values())  
        df = df.rename(columns={'category_id': 'category'}).copy()

        df['transaction_date'] = pd.DatetimeIndex(df['transaction_date']).date 

        self.daily_amor_CostColumn = 'daily_amortized_cost'
        self.amStartColumn = "am_startDate"
        self.amEndColumn="am_endDate"
        self.daysIntersectColumn="days_within"

        if filter:
            if "date_range" in filter.keys():
                self.qsd, self.qed = filter["date_range"]
            self.transactionDf = self._filter_transactions(df,filter) 
        else:
            self.transactionDf = df

    def _filter_transactions(self,df,filterDict):
        filtered_df = df 

        #filter transactions by amortization start & end dates
        if "date_range" in filterDict.keys():

            def calculate_amor_dates(am_months, date):
                # notNumpyDate = np.datetime64(date, 'D').astype(dt.datetime)
                sd,ed = Transaction(transaction_date=date, am_months=am_months)\
                    .get_amor_dates()
                return np.array([sd,ed])

            #calculates am_startDate, am_endDate, dtype: numpy datetime.date 
            x = np.vectorize(calculate_amor_dates, signature='(),()->(n)')\
                ( filtered_df['am_months'], filtered_df['transaction_date'])
            filtered_df[self.amStartColumn] = pd.DatetimeIndex(x[:,0]).date
            filtered_df[self.amEndColumn] = pd.DatetimeIndex(x[:,1]).date

            # filter for payments made whose am_sd/am_ed within [qsd, qed] (datetime.date)
            filtered_df = filtered_df.loc[(filtered_df[self.amEndColumn]>=self.qsd) &\
                                (filtered_df[self.amStartColumn]<= self.qed)].copy() 

        #filter transaction by category
        if 'category' in filterDict.keys():
            cat = filterDict['category']
            filtered_df = filtered_df.loc[
                filtered_df['category'].str\
                    .contains(cat, regex=False)].copy()   

        return filtered_df
    
    def compute_amortizationCost_column(self, amor_columnName):
        """
        calculates the total amortization cost during query period (for each transaction)
        :returns void, appends df with amortizedCostColumn, daysIntersect and 'total_cost' columns
        """
        if self.transactionDf.size ==0:
            return pd.DataFrame()

        df = self.transactionDf.copy()
    
        def calculate_amortized_cost(amount, am_months):
            return Transaction(amount=amount, am_months=am_months).compute_daily_amortized_cost()

        #add amortized_cost column to df 
        x = np.vectorize(calculate_amortized_cost)\
            (df['amount'], df['am_months']) 
        df[self.daily_amor_CostColumn] = x 

        def calculate_intersection_days(sd,ed):
            range1 = (sd,ed)
            range2 = (self.qsd, self.qed)
            return dateRange_intersection(range1, range2)
        
        #add num of intersection days within query period
        x = np.vectorize(calculate_intersection_days)\
                (df[self.amStartColumn], df[self.amEndColumn])
        
        df[self.daysIntersectColumn] = x

        #compute total amortized cost during query period
        df[amor_columnName] = df[self.daily_amor_CostColumn]*df[self.daysIntersectColumn]
        return df

class Budget_Deficit(object):

    def __init__(self):
        budget = pd.DataFrame(Budget.objects.values()) 
        budget = budget.rename(columns={
            'category_id': 'category', 
            'start_date_id': 'start_date',
            }).copy()
        budget['start_date'] = budget['start_date'].astype(str)
        self.budgetDf = budget 

    def join_budget_df(self, left_df, lefton:List[str], righton:List[str]):
        """
        @param: left_df transactionDf with lefton column fields 
        :return: new df with joined budget frame
        """
        join_bud_tran = pd.merge(left=left_df, right=self.budgetDf, \
                                left_on=lefton, right_on=righton,\
                                how='left' ) 
        return join_bud_tran

    def calculate_deficit(self, joinedDf, TMEcolumnName):
        """
        Calculates diff: monthly budget - TME
        @param: joinedDf budget, has sum_total_cost_in_period, category, monthly budget 'amount' columns
        :return: df of the diff 
        """
        joinedDf['amount'].fillna(0, inplace=True)
        joinedDf['diff'] = joinedDf['amount']-joinedDf[TMEcolumnName] 
        return joinedDf
    

class Balance_Manager(object):
    """Compiles the balance views from digesting deficit df, seeds df """

    def __init__(self, category_type):
        self.total_seed_amt_column = 'sum_seed_amount'
        self.sum_diffColumn = "sum_diff"
        self.category_type = category_type

    def sum_seeds(self)->pd.DataFrame:
        """
        :return: new df grouped by Category, summed seeds amt
        """
        seedDf = pd.DataFrame(Seed.objects.values())\
                    .rename(columns={'category_id': 'category'})
        sum_seeds_df = seedDf.groupby('category')['amount'].agg(['sum']).reset_index()
        return sum_seeds_df.rename(columns={'sum': self.total_seed_amt_column})

    def calculate_ytd_balance(self, tran_diff_df, months_column:str, seedDf)->pd.pivot_table:
        """
        @param: tran_diff_df contains the columns: diff, months column,  of all the months ytd
        :return: dataframe: running monthly balance of the categorial account 
        """
        df_new = tran_diff_df[tran_diff_df['category'].isin(CategoryCollection.get_accum_categories_by_type(self.category_type))]

        #using a pivot table to calculate sum of all ytd diffs 
        pvt = pd.pivot_table(df_new, values='diff', index='category', \
                columns=[months_column], aggfunc=np.sum)
        pvt.fillna(0, inplace=True)
        pvt[self.sum_diffColumn] = pvt.sum(axis=1)
        join_diff_seedDf = pd.merge(pvt, seedDf, left_on='category', right_on='category', how='left')
        join_diff_seedDf.fillna(0, inplace=True)
        # join_diff_seedDf[self.balanceColumn] = join_diff_seedDf.sum(axis=1)
        print("join_diff_seedDf: \n", join_diff_seedDf.head())
        return [pvt.drop(self.sum_diffColumn, axis=1), \
                    join_diff_seedDf[['category', 
                        self.sum_diffColumn, self.total_seed_amt_column]] ]

    def report_running_diff_and_balance(self, categoriesList=None)->List[pd.DataFrame]:
        qsd = datetime.date(2018,5,1) #TODO start of budget records 
        qed = datetime.datetime.today().date()

        # generate all months, all category 'diff' column
        ta = Transaction_Manager(filter={
                        "date_range": [qsd, qed],
                        "category": ''   }, \
                        category_type=self.category_type) 
        transaction_amorDf = ta.generate_amorCostDf_all()
        if transaction_amorDf.size > 0:
            category_gpDf = ta.compute_aggregateSums(transaction_amorDf)
            bs = Budget_Deficit()
            transaction_budget_joined = bs.join_budget_df(category_gpDf, \
                    lefton=[ta.amor_dateColumn, 'category'],\
                    righton=['start_date', 'category'])
            transaction_with_diff = bs.calculate_deficit(transaction_budget_joined, ta.total_amor_cost)

            diff_pivotDf, balanceDf = self.calculate_ytd_balance(transaction_with_diff, ta.amor_dateColumn, self.sum_seeds())
            return [diff_pivotDf, balanceDf]
        else:
            return [pd.DataFrame(), pd.DataFrame()]






                            


