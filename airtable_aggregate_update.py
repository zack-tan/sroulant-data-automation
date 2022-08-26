""" Airtable Client Aggregate Table Update script
Developed by Zack Tan (https://bit.ly/linkedin-zacktan) for Santropol Roulant

This script updates the client-level aggregated table in Sous-Chef 
"""
from pyairtable import Table
from collections import defaultdict
from typing import Dict
import sys

CREDENTIALS_FILE = 'credentials.txt'

''' 
Reads a text file and stores credentials for Sous-chef & Airtable as a dict to be used later.

Params:
    cred_file - a text file of credentials, separated by newline and in the format <param>=<value>

Returns: A dict with format - { 'parameter' : 'value' }
'''
def read_credentials(cred_file) -> Dict[str, str]:
    return_dict = {}
    try:
        with open(cred_file, mode = 'r', encoding = "utf8") as credentials:
            while True:
                return_dict['BASE_URL'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['USERNAME_SC'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['PASSWORD_SC'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['API_KEY'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['BASE_ID'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['BASE_NAME'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['TABLE_NAME_AGG'] = credentials.readline().split("=",1)[1].rstrip().lstrip()
                return_dict['TABLE_NAME_MONTHLY'] = credentials.readline().split("=",1)[1].rstrip().lstrip()

                credentials.close()
                
                return return_dict
    except FileNotFoundError:
        print(f"Credentials file not found! Please check that 'credentials.txt' is located in the same folder as this script then run again.")
        return

if __name__ == '__main__':
    print("\nThis script was built for Santropol Roulant and will refresh the client-level meal aggregate table on Airtable.")
    print("\nSource code can be found on github at: https://bit.ly/sroulant-automation")

    input("\nPlease ensure the credentials file 'credentials.txt' is updated and stored in the same directory as this script. More info can be found on Github.\nPress Enter to continue.")

    creds = read_credentials()
    if not creds:
        input("Press Enter to finish.")
        sys.exit()

    API_KEY = creds['API_KEY']
    BASE_ID = creds['BASE_ID']
    BASE_NAME = r'(McGill) 2022 Clients data and meals data' if not creds['BASE_NAME'] else creds['BASE_NAME']
    TABLE_NAME_AGG = r'Client_Aggregates' if not creds['TABLE_NAME_AGG'] else creds['TABLE_NAME_AGG']
    TABLE_NAME_MONTHLY = r'Client_Count_Monthly_2022' if not creds['TABLE_NAME_MONTHLY'] else creds['TABLE_NAME_MONTHLY']

    print(f"\nConnecting to tables {TABLE_NAME_AGG} and {TABLE_NAME_MONTHLY} on Base ID {BASE_ID} @ Airtable...")

    # Initialize Airtable API connector
    table = Table(API_KEY, BASE_ID, TABLE_NAME_MONTHLY)
    table_agg = Table(API_KEY, BASE_ID, TABLE_NAME_AGG)

    # Retrieve all entries from client_count_monthly and aggregation table
    try:
        table_rows = table.all()
        aggregation_rows = table_agg.all()
    except:
        print(f"\nUnable to connect to specified tables. Please check the provided table names again and re-run this script after verifying.")
        input("Press Enter to finish.")
        sys.exit()

    print("\nSuccessfully connected.\n")



    ### TALLY AGAINST CLIENT_COUNT_MONTHLY TO CHECK IF NEW RECORDS EXIST (i.e. new clients)

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

    try:
        [table_agg.create({ 'Name': n, 'Update': False}) for n in missing_names]
    except:
        print(f"Unable to write new records into {TABLE_NAME_AGG}. Please check that required columns exist and are of the correct type:")
        print("'Name' of type Single line text.")
        print("'Update' of type Checkbox.")
        input("\nRun this script again after verifying. Press Enter to finish.")
        sys.exit()

    # Recollect the total number of rows in aggregated table and store Airtable IDs of retrieved records
    aggregation_rows = table_agg.all()
    records = [r.get('id') for r in aggregation_rows]
    
    # Refresh all records - Works with an automation built within Airtable
    try:
        for i, r in enumerate(records):
            # Uncheck all Update boxes and clear lookup records
            table_agg.update(record_id = r, fields = {'Update': False, 'Lookup': ''})

            # Check all Update boxes to activate automation
            table_agg.update(record_id = r, fields = {'Update': True})
            
            print(f"Refreshed {i+1} out of {len(records)} entries.")

        input("Operation completed. Press Enter to finish.")
    except:
        print("Unable to refresh records. Please check that column names match and are of the correct type:")
        print("'Update' of type Checkbox.")
        print("'Lookup' of type Linked Field (multiple).")
        print("\nRun this script again after verifying.")
    
