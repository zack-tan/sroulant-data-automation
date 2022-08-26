""" Sous-Chef Billing Data Web Scraper 
Developed by Zack Tan (https://bit.ly/linkedin-zacktan) for Santropol Roulant

This script uses Selenium to traverse the Sous-Chef platform (https://github.com/savoirfairelinux/sous-chef) and retrieve billing details for the most recent month.
It then writes these records into the Roulant's Airtable DB.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from collections import defaultdict
from pyairtable import Table
from typing import Dict
from selenium.common.exceptions import WebDriverException
import pandas as pd
import sys

# Initialization
CREDENTIALS_FILE = "credentials.txt"

print("\nThis script was built for Santropol Roulant and will log onto the Sous-Chef website to scrape meal data for the latest month, before writing the same into Airtable")
print("\nSource code for the file can be found on github at: https://bit.ly/sroulant-automation")

print("\nPlease ensure the following:\n- You are logging in from the roulant or connected to the organization's VPN.\n- the file 'credentials.txt' is updated and located in the same directory as this script.")
input("Press Enter to continue.")

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


# Get WebDriver and start maximized
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(r'C:\Users\tanzc\chromedriver.exe', chrome_options=options)

if __name__ == '__main__':

    creds = read_credentials(CREDENTIALS_FILE)

    if not creds:
        print(f"Credentials file not found! Please check that 'credentials.txt' is located in the same folder as this script then run again.")
        input("Press Enter to finish.")
        sys.exit()

    BASE_URL = r"https://sous-chef.office.santropolroulant.org/p/login?next=/" if not creds['BASE_URL'] else creds['BASE_URL']
    USERNAME_SC = creds['USERNAME_SC']
    PASSWORD_SC = creds['PASSWORD_SC']

    API_KEY = creds['API_KEY']
    BASE_ID = creds['BASE_ID']
    BASE_NAME = r'(McGill) 2022 Clients data and meals data' if not creds['BASE_NAME'] else creds['BASE_NAME']
    TABLE_NAME = r'Client_Count_Monthly_2022' if not creds['TABLE_NAME_MONTHLY'] else creds['TABLE_NAME_MONTHLY']
    
    try:
        driver.get(BASE_URL)
    except WebDriverException:
        print(f"\nUnable to connect to Sous-chef. Please ensure you're connected to the VPN then re-run this script.")
        input("Press Enter to finish.")
        sys.exit()

    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, r"id_username")))

    ### SC LOGIN PAGE

    # Enter credentials
    userbox = driver.find_element_by_id(r"id_username")
    userbox.click()
    userbox.send_keys(USERNAME_SC)

    passbox = driver.find_element_by_id(r"id_password")
    passbox.click()
    passbox.send_keys(PASSWORD_SC)

    # Click login
    driver.find_elements_by_xpath(r"(//a[@href='/billing/list/'])")
    actions = ActionChains(driver)
    actions.send_keys(Keys.RETURN)
    actions.perform()


    ### SC HOME PAGE

    # Find billing icon and click to go into billing page
    billing_icons = driver.find_elements_by_xpath(r"(//a[@href='/billing/list/'])")
    billing_icons[1].click()            # Need to use the 2nd element. 1st is unaccessible for some reason
    
    '''
    Oldest month is November 2017. List of WebElements returned is in opposite order:
    - x[0] is the latest month. Need to think of a way to reverse the order
    - y list has 2 extra elements at the start, from title. Need to drop these
    '''

    ### BILLING SUMMARY PAGE

    # Returns all clickable 'view' eyeball links that open the invoices
    x = driver.find_elements_by_xpath(r"//a[contains (@href, '/billing/view/')]")
    y = driver.find_elements_by_xpath(r"//a[contains (@href, '/billing/view/')]//preceding::strong")
    
    # Remove first 2 elements of label list - Those are elements elsewhere in the table
    y = y[2:]
   
    # Store corresponding month label
    month = y[0].text.split()[0]

    # Use latest month
    x[0].click()


    ### INDIVIDUAL MONTH BILLING PAGE

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, r"sc_bs")))

    table_data = driver.find_element_by_id(r"sc_bs")
    rows = table_data.find_elements_by_tag_name('tr')

    # rows[0] is always the table headers -> "NEW CLIENT NAME DELIVERY STATUS PAYMENT METHOD PRICE SCALE ...."
    # rows[1] is always the subheaders -> "Regular Large"
    rows = rows[2:]

    # Other data format as follows:
    # '<lastname>, <firstname> <Episodic/Ongoing> ---- <Low income / blank> <n_orders> <n_regmeals / blank> <n_largemeals / blank> <n_extra / blank> <Total_amt_in_dollars>'

    #client_info = dict.fromkeys(['name', 'delivery_status', 'payment_method', 'price_scale', 'n_orders', 'meals_reg', 'meals_large', 'meals_extra', 'total'], [])
    client_info = defaultdict(list)
    
    ''' td cell references
    0 - blank
    1 - lastname, firstname
    2 - Ongoing / Episodic
    3 - Payment method
    4 - Low Income / blank
    5 - No. orders
    6 - Reg Meals
    7 - Large Meals
    8 - Extra Side Dishes
    9 - Income
    10 - blank
    '''

    count = 0
    for i, entry in enumerate(rows):
        cells = entry.find_elements_by_tag_name('td')
        
        # Skip anything that isn't data
        if len(cells) < 11:
            continue
        
        client_info['name'].append(cells[1].text)
        client_info['delivery_status'].append(cells[2].text)
        client_info['payment_method'].append(cells[3].text)
        client_info['price_scale'].append(cells[4].text)
        client_info['n_orders'].append(cells[5].text)
        client_info['meals_reg'].append(cells[6].text)
        client_info['meals_large'].append(cells[7].text)
        client_info['meals_extra'].append(cells[8].text)
        client_info['total'].append(cells[9].text)

        count += 1
        print(f"Scraped {count} rows.")
    
    # Close Selenium 
    driver.quit()

    print("\nScraping completed. Processing data...")

    ### PANDAS PROCESSING HERE    
    df = pd.DataFrame.from_dict(client_info)

    # Replace blank price scales with regular
    df['price_scale'] = df['price_scale'].replace("", "Regular")
    df['meals_reg'] = df['meals_reg'].replace('', 0)
    df['meals_large'] = df['meals_large'].replace('', 0)
    df['meals_extra'] = df['meals_extra'].replace('', 0)

    # Remove dollar sign from total - then convert to float type
    df['total'] = df['total'].str[1:]
    
    df['total'] = df['total'].astype(float)
    df['n_orders'] = df['n_orders'].astype(int)
    df['meals_reg'] = df['meals_reg'].astype(int)
    df['meals_large'] = df['meals_large'].astype(int)
    df['meals_extra'] = df['meals_extra'].astype(int)

    # Insert new column corresponding to month
    df.insert(1, 'month', month)

    # Export out to csv for further processing
    df.to_csv(f"{month}_cleaned.csv",index=False)
    print(f"Data processed. Output to file: {month}_cleaned.csv.")
    

    ### CONNECT AND WRITE TO AIRTABLE
    print("\nNow writing to Airtable...")

    # print(f"\nPaste Base ID to use and hit Enter. For more information, refer to: https://support.airtable.com/hc/en-us/articles/4405741487383-Understanding-Airtable-IDs")
    # base_id = input(fr"Alternatively, leave blank to use default '{BASE_NAME}': ")
    
    # table_name = input(f"\nPlease specify the NAME of the table containing monthly client meal data. Leave blank to use default '{TABLE_NAME}': ")

    # if base_id == '':
    #     base_id = BASE_ID
    # if table_name == '':
    #     table_name = TABLE_NAME

    print(f"\nConnecting to table {TABLE_NAME} on Base ID {BASE_ID} @ Airtable...")

    table = Table(API_KEY, BASE_ID, TABLE_NAME)

    try:
        table.all()
    except:
        print(f"\nUnable to connect to {TABLE_NAME}. Please check that the correct table name has been given and re-run this script after verifying.")
        input("Press Enter to finish.")
        sys.exit()

    print("\nSuccessfully connected.\nWriting to table...\n")

    try:
        for i, row in df.iterrows():
            table.create({ 'CLIENT NAME': row['name'], 'MONTH': row['month'], 'Delivery status': row['delivery_status'], 'Price scale': row['price_scale'],
                            'Number of orders': row['n_orders'], 'Meals reg': row['meals_reg'], 'Meals large': row['meals_large'], 
                            'Extra': row['meals_large'], 'Montant facture': row['total']
            })

            print(f"Wrote {i+1} out of {len(df)} records")
    except:
        print(f"Unable to write new records into {table_name}. Please check that the required columns exist and are of the correct type:")
        print("'CLIENT NAME' of type Single line text.")
        input("\nRun this script again after verifying. Press Enter to finish.")
        sys.exit()


    print("\nFinished writing to Airtable. If you wish to refresh the client aggregate table, please run the other script 'airtable_aggregate_update.exe'.")
    input("Press Enter to finish.")