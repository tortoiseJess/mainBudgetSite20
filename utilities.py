import datetime
import locale
from typing import List 
import math, random

def cal_elasped_amortized_days(am_sd, am_ed, qsd, qed)->int:
    """
    Calculate the number of days in query period that falls w/i amortization period
    Note: used to calculate  total amortization amt within the query period
    :param am_sd: DateTime: amortization start day
    :param am_ed: DateTime: amortization end day
    :param qsd: DateTime: query start day
    :param qed: DateTime: query end day
    """
    if qed < am_sd or qsd > am_ed:
        return 0
    return abs(max(qsd,am_sd)-min(qed, am_ed))

def generate_months_btw(qsd:datetime.date,qed:datetime.date)->List[str]:
    """
    :returns list of months within qsd, qed inclusive
    included months as strings: eg. 2019-05
    ref: https://stackoverflow.com/a/34898764
    """

    total_months = lambda dt: dt.month + 12 * dt.year
    mlist = []
    for tot_m in range(total_months(qsd) - 1, total_months(qed)):
        y, m = divmod(tot_m, 12)
        mlist.append(datetime.datetime(y, m + 1, 1).strftime("%Y-%m"))
    return mlist

def format_currency(val:float, dp=2)->str:
    """
    eg -344352.35835 --> '($344,352.36)'
    using USD 
    """
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    cur=locale.currency(round(val,dp), grouping=True)
    return cur

def dateRange_intersection(r1: datetime.date, r2: datetime.date)->int:
    """
    calculates intersection as number of DAYS 
    note: if return <0 means there is no intersection, 
          added 1 day to final result
    """
    s1,e1=r1
    s2,e2=r2
    if s1>e1 or s2>e2:
        raise ValueError("start dates must be < end dates in daterange arguments")
    s_ints = max(s1,s2)
    e_ints = min(e1,e2)
    ints_days= (e_ints-s_ints).days

    if ints_days>=0:
        return ints_days +1
    else:
        return ints_days

def multi_index_2_dict(df)->dict:
    """
    @param df: pd dataframe/series with multi-index levels >=2
    :return: expands the multiindex keys into nested dict keys
    """
    dik = {}

    for key1 in df.index.get_level_values(0):
        dik[key1]={}
        for key2 in df.loc[key1].index.get_level_values(0):
            dik[key1][key2] = df.loc[key1][key2]
    return dik

def get_next_month(prev=False)->datetime.date: 
    """returns the first date of next month"""
    today = datetime.date.today()
    if not prev:
        first_day = today.replace(day=1, month=today.month+1) 
    else:
        first_day = today.replace(day=1, month=today.month-1)
    return first_day

def get_rand_hex_color(multiplier=200):
    r = math.floor(random.random() * multiplier)
    g = math.floor(random.random() * multiplier)
    b = math.floor(random.random() * multiplier)
    color = '#%02x%02x%02x' % (r, g, b)
    return color