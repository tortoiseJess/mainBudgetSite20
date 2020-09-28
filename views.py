from django.shortcuts import render
import json 
from business import Balance_Manager


def appIndex(request):
    return render(request, "contents_page.html", \
                context={"nm_year": get_next_month().year,\
                        "nm_month": get_next_month().month 
                        })

def balance_viewer(request, category_type):
    bv = Balance_Manager(category_type)
    diff_df, balance_df = bv.report_running_diff_and_balance()

    diff_html = diff_df.to_html(float_format=(lambda x:'${:.2f}'.format(x)), justify="right")
    balance_html = balance_df.to_html(float_format=(lambda x:'${:.2f}'.format(x)), justify="right")
    
    #data for bar chart 
    diff_json = balance_df[['category', 'sum_diff']].to_json(double_precision=2)
    print(diff_json)
    
    return render(request, "budget/balance.html",
                {
                    'diff_table': diff_html,
                    'balance_table': balance_html,
                    'houseSupply_diff_datas': list(diff_df.loc['house supply',:]),
                    'table_labels':list(diff_df.columns),
                    'balances_json':json.dumps(diff_json),
                }
        )