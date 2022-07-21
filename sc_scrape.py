import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

# Initialization
BASE_URL = r"https://sous-chef.office.santropolroulant.org/p/login?next=/"
USERNAME_SC = r'xx'
PASSWORD_SC = r'xx'
MONTH = r'June 2022'

results = []

# Get WebDriver 
# Start maximized

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(r'C:\Users\tanzc\chromedriver.exe', chrome_options=options)

##### ENSURE CONNECTION TO VPN AND ABLE TO ACCESS SC NORMALLY #####

if __name__ == '__main__':

    # TODO: Prompt user to check if VPN is engaged
    
    driver.get(BASE_URL)

    # TODO: Check if already logged in
    
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

    # TODO: Check if dollar icon is visible. If screen is smaller, need to expand button first

    ### SC HOME PAGE

    # Find billing icon and click to go into billing page
    billing_icons = driver.find_elements_by_xpath(r"(//a[@href='/billing/list/'])")
    billing_icons[1].click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, r"dollar icon")))
    
    billing_icon = driver.find_element_by_class_name(r"dollar icon")
    billing_icon.click()


    # TODO: Change to XPath, much better that way
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, r"ui popup calendar bottom left transition hidden")))
    
    # Class 
    # unhide button class 'icon unhide'
    show_invoice = driver.find_element_by_class_name(r"icon unhide")

    pass

