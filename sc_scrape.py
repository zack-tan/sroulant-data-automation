""" Sous-Chef Billing Data Web Scraper 
Developed by Zack Tan (https://bit.ly/linkedin-zacktan) for Santropol Roulant, 2022

This script uses Selenium to traverse the Sous-Chef platform (https://github.com/savoirfairelinux/sous-chef) and retrieve billing details for the most recent month.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from collections import defaultdict

import pandas as pd

# Initialization
BASE_URL = r"https://sous-chef.office.santropolroulant.org/p/login?next=/"
USERNAME_SC = r'xx'
PASSWORD_SC = r'xx'
month = r'-'

print("\nThis script was built for Santropol Roulant and will log onto the Sous-Chef website and scrape meal data for the latest month.")
print("Source code for the file can be found on github at: https://github.com/zack-tan/sroulant-sc_scraper-airtable-link")

input("\nPlease ensure you are logging in from the roulant or connected to the organization's VPN before continuing. Press Enter to continue.")

# Get WebDriver and start maximized
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(r'C:\Users\tanzc\chromedriver.exe', chrome_options=options)

if __name__ == '__main__':

    driver.get(BASE_URL)
    
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
    #login = driver.find_element_by_class_name(r"ui fluid large yellow button").click()
    #x = driver.find_elements_by_xpath(r"(//button[@class='ui fluid large yellow button'])")
    #x[0].click()
    driver.find_elements_by_xpath(r"(//a[@href='/billing/list/'])")
    #driver.find_element_by_name("Value").send_keys(Keys.RETURN)
    actions = ActionChains(driver)
    actions.send_keys(Keys.RETURN)
    actions.perform()


    ### SC HOME PAGE

    # Find billing icon and click to go into billing page
    billing_icons = driver.find_elements_by_xpath(r"(//a[@href='/billing/list/'])")
    billing_icons[1].click()            # Need to use the 2nd element. 1st is unaccessible for some reason
    
    # //a[contains (@title,'公司债券') and not(contains(@title,'短期')) ]
    # //a[contains (@class,'btnX') and .//text()='Sign in']
    # //a[contains (@href, '/billing/view/')]
    # //a[contains (@href, '/billing/view/')] - Works
    
    '''
    Oldest month is November 2017. List of WebElements returned is in opposite order:
    - x[0] is the latest month. Need to think of a way to reverse the order
    - y list has 2 extra elements at the start, from title. Need to drop these
    '''

    ### BILLING SUMMARY PAGE

    # TODO: Some kind of wait for load

    # Returns all clickable 'view' eyeball links that open the invoices
    x = driver.find_elements_by_xpath(r"//a[contains (@href, '/billing/view/')]")
    y = driver.find_elements_by_xpath(r"//a[contains (@href, '/billing/view/')]//preceding::strong")
    
    # Remove first 2 elements of label list - Those are elements elsewhere in the table
    y = y[2:]
   
    # Store corresponding month label
    month = y[0].text.split()[0]        

    # Use latest month
    x[0].click()
    

    '''
    # TODO: Reverse both lists to allow for easier estimation
    x.reverse()
    y.reverse()
    
    # To take in input in form of "xxx yyyy" where xxx is month and yyyy is year
    offset = -1
    if month == 'dec':
        pass
    elif month == 'jan':
        pass
    '''

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
        # client_info.setdefault('name').append(cells[1].text)
        # client_info.setdefault('delivery_status').append(cells[2].text)
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

    # 2 methods to remove dollar sign from total - then convert to float type
    #df['total'] = df['total'].apply(lambda x: x[1:]) 
    df['total'] = df['total'].str[1:]
    
    df['total'] = df['total'].astype(float)

    # Insert new column corresponding to month
    df.insert(1, 'month', month)

    # @Laura: What do you want to do with '----' in Payment Method?

    # Export out to csv for further processing
    df.to_csv(f"{month}_cleaned.csv",index=False)

    print(f"Data processed. File output: {month}_cleaned.csv.")
    
