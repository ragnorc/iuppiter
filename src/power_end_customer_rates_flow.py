from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
from datetime import datetime
import json
from utils import write_to_db


def get_end_customer_rates_check24(zipcode, consumption, csv=False):

    """
        Scrapes Data from the check24 website.
     Returns the end customer rates associated with each
     electricity tariff on check24 as pandas dataframe. saves it into a
     csv file if csv=True,
     takes as input the zipcode and annual consumption in kWh as string

    """

    #validate_zipcode(zipcode)
    #validate_consumption(consumption)

    url = 'https://www.check24.de/strom/vergleich/check24/?pid=24&zipcode={}&totalconsumption={}&contractperiod_toggle=12&considerdiscounts=yes&maxbonusshare=yes&eco=no&eco_type=normal&priceguarantee=fixed_price&priceguarantee_months=12&companyevaluation_positive=yes&customertype=private&contractperiod=12&cancellationperiod=42&pagesize=500'.format(zipcode, consumption)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)

    time.sleep(2)

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

    query_dt = datetime.utcnow()

    time.sleep(9)  # Wait until all results are loaded and pop up disappears

    # scoll down to the bottom of the page  and load additional results,
    # until every result is visible

    driver.refresh()
    provider_price_details = driver.find_elements_by_class_name(
            'ajax-pricelayer')

    data = [provider.get_attribute('textContent').split()
                for provider in provider_price_details]

    driver.quit()  # Close browser

    df = pd.DataFrame()

    # Process Data and append to dataframe
    df['grossHourlyRate'] = [
            float(e[e.index('Arbeitspreis') + 5].replace(',', '.'))
            if 'Arbeitspreis' in e else None for e in data
        ]

    df['grossBaseRate'] = [
            float(e[e.index('Grundpreis') + 3].replace(',', '.'))
            if 'Grundpreis' in e else None for e in data

        ]

    df['netHourlyRate'] = [
            float(e[e.index('Arbeitspreis') + 6].replace(',', '.').replace('(', '').replace(')', ''))
            if 'Arbeitspreis' in e else None for e in data
        ]

    df['netBaseRate'] = [
            float(e[e.index('Grundpreis') + 4].replace(',', '.').replace('(', '').replace(')', ''))
            if 'Grundpreis' in e else None for e in data

        ]

    df['appliesFrm'] = [
            (datetime.strptime(e[e.index('gultig')+2],
                               '%d.%m.%Y.').date()).strftime('%Y-%m-%d')
            if 'gultig' in e else None for e in data
        ]

    df['immediateBonus'] = [
            float(e[e.index('Sofortbonus')+1].replace(',', '.'))
            if 'Sofortbonus' in e else None for e in data
        ]

    df['newCustomerBonus'] = [
            float(e[e.index('Neukundenbonus')+1].replace(',', '.'))
            if 'Neukundenbonus' in e else None for e in data
        ]

    df['city'] = [data[1][5]]*len(data)
    df['source'] = ['check24']*len(data)
    df['sourceUrl'] = [url]*len(data)
    df['productType'] = ['power']*len(data)
    df['loadProfile'] = ['H0']*len(data)
    df['maxContractDuration'] = [12]*len(data)
    df['zipcode'] = [zipcode]*len(data)
    df['consumption'] = [int(consumption)]*len(data)
    df['date'] = datetime.today().date().isoformat()
    df['rank'] = df.index

    print(df)
    return df

for zipcode in [53604, 49090, 73312]:
    for consumption in [1500 ,2500 ,4000 ,5500,10000]:
        end_customer_rates = get_end_customer_rates_check24(zipcode, consumption)
        write_to_db(json.loads(end_customer_rates.to_json(orient='records')), "EndCustomerRate", "end_customer_rate_unique", ["date", "rank", "zipcode", "consumption", "loadProfile"])
