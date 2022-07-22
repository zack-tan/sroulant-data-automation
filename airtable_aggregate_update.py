""" Client Aggregate Table Update script
Developed by Zack Tan (https://bit.ly/github-zack) for Santropol Roulant 


"""
import pyairtable as pyat
from pyairtable import Api, Base, Table
from pyairtable import formulas as fm
import pandas as pd

API_KEY = 'xx'
BASE_ID = 'xx'

if __name__ == '__main__':
    # api = Api('key2RncEIzaX4d00l')
    # api.all('base_id', 'table_name')
    # base = Base('apikey', 'base_id')
    # base.all('table_name')

    # Read in data to import
    df = pd.read_csv("latest_month_cleaned.csv")

    # Initialize Airtable API connector
    table_agg = Table(API_KEY, BASE_ID, 'Client_Aggregates')

    # Retrieve all records from aggregation table
    aggregation_rows = table_agg.all()

    # Store Airtable IDs of retrieved records
    records = []
    for r in aggregation_rows:
        records.append(r.get('id'))

    # Refresh all records - Works with an automation built within Airtable
    for i, r in enumerate(records):
        # Uncheck all Update boxes and clear lookup records
        table_agg.update(record_id = r, fields = {'Update': False, 'Lookup': ''})

        # Check all Update boxes to activate automation
        table_agg.update(record_id = r, fields = {'Update': True})
        
        print(f"Refreshed {i+1} out of {len(records)} entries.")
    
    print("Operation completed")