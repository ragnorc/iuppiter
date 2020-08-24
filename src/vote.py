from time import sleep
from seleniumwire import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
from datetime import datetime
import json
from utils import write_to_db


def vote():

    """
        Scrapes Data from the check24 website.
     Returns the end customer rates associated with each
     electricity tariff on check24 as pandas dataframe. saves it into a
     csv file if csv=True,
     takes as input the zipcode and annual consumption in kWh as string

    """

    #validate_zipcode(zipcode)
    #validate_consumption(consumption)

    url = 'https://www.easypolls.net/poll.html?p=5f43abace4b0065ae3b4a35c'

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1420,1080')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, seleniumwire_options={
'proxy': {
    'http': 'http://auto:MomRfo8iFBxvLzYSLdhvdjS6z@proxy.apify.com:8000',
    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
    }
})
    driver.get(url)
    driver.delete_all_cookies()

#    try:
#        cookie_button = driver.find_element_by_class_name(
#            'c24-cookie-button')

#        cookie_button.click()

#    except ElementNotInteractableException:
#        pass
        

    #zipcode_input = driver.find_element_by_id('c24api_zipcode')
    #zipcode_input.clear()
    #zipcode_input.send_keys(zipcode)
    #driver.execute_script("document.getElementById('c24api_zipcode').value="+str(zipcode))


    #consumption_input = driver.find_element_by_id('c24api_totalconsumption')
    #driver.execute_script("document.getElementById('c24api_totalconsumption').value=''")
    #consumption_input.clear()
    #consumption_input.send_keys(consumption)
    #driver.execute_script("document.getElementById('c24api_totalconsumption').value="+str(consumption))


    #compare_button = driver.find_element_by_id('c24_calculate')
    #compare_button.click()

    driver.execute_script("document.getElementById('l_11_5f43abace4b0065ae3b4a35c').click(); document.getElementById('OPP-poll-vote-button').click();")
    driver.delete_all_cookies()
    driver.quit()  # Close browser

def loo():
    for i in range(0,21):
        try:
            vote()
        except:
            print(i)

loo()
