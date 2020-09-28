# main BudgetSite20

 A budget app that tracks spending + plans budget.
 - Added amortization calculations.
 - Uses Django framework, postgres 

 Main files:
 -----------
 - models.py 

  Data modelling (see model_er.drawio)
  ![ER drawing](https://github.com/tortoiseJess/budgetSite20/blob/master/drawio.PNG)

 - budget_business /business.py:

 Contains logic to draw data from postgres database.
 Pandas does all the heavy lifting statistical calculations

 - budget_views/ views.py

 Handles requests + converts dataframe to html


 On going todo list:
 1. Add in d3 charts for quick summary visualizations
 2. Integrate with ocr read receipt feature 
 3. Optimization
