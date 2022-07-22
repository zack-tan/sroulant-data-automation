""" Client Aggregate Table Update script
Developed by Zack Tan (https://bit.ly/github-zack) for Santropol Roulant 


"""
import pyairtable as pyat
from pyairtable import Api, Base, Table
from pyairtable import formulas as fm
import pandas as pd
from collections import defaultdict

API_KEY = 'xx'
BASE_ID = 'xx'

if __name__ == '__main__':

    # Read in data to import
    df = pd.read_csv("latest_month_cleaned.csv")

    # Initialize Airtable API connector
    table = Table(API_KEY, BASE_ID, 'Client_Count_Monthly')
    table_agg = Table(API_KEY, BASE_ID, 'Client_Aggregates')


    ### TALLY AGAINST CLIENT_COUNT_MONTHLY TO CHECK IF NEW RECORDS EXIST (i.e. new clients)

    # Retrieve all entries from client_count_monthly and aggregation table
    table_rows = table.all()
    aggregation_rows = table_agg.all()

    # Store month-by-month data into a defaultdict - {name : [corresponding airtable_record_IDs]} 
    name_id_dict = defaultdict(list)
    for t in table_rows:
        client_name = t.get('fields').get('CLIENT NAME')
        name_id_dict[client_name].append(t.get('id'))

    # Get list of all names for both aggregate and month-by-month tables
    name_list_monthly = list(name_id_dict.keys())
    name_list_agg = [r.get('fields').get('Name') for r in aggregation_rows]

    # Check that all names in month-by-month appears in aggregate table too. If not, write those records into the aggregates table
    # Format of output defaultdict - { 'Name' : [Airtable Record IDs] }
    name_id_missing = defaultdict(list)

    for n in name_list_monthly:
        if n not in name_list_agg:
            name_id_missing[n] = name_id_dict.get(n)

    # Add missing records into aggregate table
    missing_names = list(name_id_missing.keys())

    # for n in missing_names:
    #     table_agg.create({ 'Name': n, 'Update': False })
    [table_agg.create({ 'Name': n, 'Update': False}) for n in missing_names]
    
    
    # Recollect the total number of rows in aggregated table and store Airtable IDs of retrieved records
    aggregation_rows = table_agg.all()
    records = [r.get('id') for r in aggregation_rows]
    
    # Refresh all records - Works with an automation built within Airtable
    for i, r in enumerate(records):
        # Uncheck all Update boxes and clear lookup records
        table_agg.update(record_id = r, fields = {'Update': False, 'Lookup': ''})

        # Check all Update boxes to activate automation
        table_agg.update(record_id = r, fields = {'Update': True})
        
        print(f"Refreshed {i+1} out of {len(records)} entries.")
    
    print("Operation completed.")