# Core Banking Ledger Database CPU Capacity Forecast and Auto-Scaling Pipeline

Forecasts a database server's CPU 5, 15 and 30 minutes ahead and adds cores before an overload happens.

## Result
On 22 days of unseen test data, overload minutes fell from 960 (no scaling) to 16 with predictive scaling. That is 68% fewer than reactive scaling (50), using about 4.5% of the extra cores that always running 8 cores would need.

## How it works
MySQL (customers, accounts, transactions and a per-minute view) -> Python (features, XGBoost and LightGBM, scaling rules) -> log table in MySQL -> Power BI dashboard.

## Files
- load_transactions_mysql_v2.py: reloads the transactions with generated timing
- Capstone_v2.ipynb: the full pipeline, cell by cell
- Figures/: charts from the notebook
- Capstone_Bank_Dashboard.pdf: export of the Power BI dashboard
- Capstone_Final_Presentation_v3.pptx: project slides

## How to run
1. Create the tables and the view in MySQL (database bank_db).
2. Put customers.csv, accounts.csv and transactions_inserts.sql in the Data folder (not included because of their size).
3. Put your MySQL password where the files say MY_PASSWORD.
4. Run: python load_transactions_mysql_v2.py
5. Open Capstone_v2.ipynb and run all cells, then refresh the Power BI dashboard.

## Data note
The 1,000,000 transactions come from a Kaggle dataset. Their timing, the random load events and the CPU are simulated.

## Limitations
Sudden events cannot be predicted. The test period has only 11 overload episodes. The 30-minute forecast alone is not enough, so the 5-, 15- and 30-minute forecasts are combined.

Author: Bhargavi PR
