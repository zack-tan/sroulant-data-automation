""" Airtable Client Aggregate Table Update script
Developed by Zack Tan (https://bit.ly/github-zack) for Santropol Roulant

This script updates the client-level aggregated table in Sous-Chef 
"""
from pyairtable import Api, Base, Table
from pyairtable import formulas as fm
import pandas as pd
from collections import defaultdict

API_KEY = 'xx'
BASE_ID = 'xx'
BASE_NAME = r'(McGill) 2022 Clients data and meals data'
TABLE_NAME_AGG = r'Client_Aggregates'
TABLE_NAME_MONTHLY = r'Client_Count_Monthly_2022'

if __name__ == '__main__':
    print("\nThis script was built for Santropol Roulant and will refresh the client-level meal aggregate table on Airtable.")
    print("\nSource code for the file can be found on github at: https://github.com/zack-tan/sroulant-sc_scraper-airtable-link")

    print(f"\nPaste Base ID to use and hit Enter. For more information, refer to: https://support.airtable.com/hc/en-us/articles/4405741487383-Understanding-Airtable-IDs")
    base_id = input(fr"Alternatively, leave blank to use default '{BASE_NAME}': ")
    
    table_name_agg = input(f"\nPlease specify the NAME of the table containing client-level aggregated meal data. Leave blank to use default '{TABLE_NAME_AGG}': ")
    table_name_monthly = input("\nPlease specify the NAME of the table containing month-level client meal data (used for tallying). \ "
                                f"Leave blank to use default '{TABLE_NAME_MONTHLY}': ")

    if base_id == '':
        base_id = BASE_ID
    if table_name_agg == '':
        table_name_agg = TABLE_NAME_AGG
    if table_name_monthly == '':
        table_name_monthly = TABLE_NAME_MONTHLY

    print(f"\nConnecting to tables {table_name_agg} and {table_name_monthly} on Base ID {base_id} @ Airtable...")

    # Initialize Airtable API connector
    table = Table(API_KEY, BASE_ID, table_name_monthly)
    table_agg = Table(API_KEY, base_id, table_name_agg)

    print("\nSuccessfully connected.\n")


    

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
    
    input("Operation completed. Press Enter to finish.")