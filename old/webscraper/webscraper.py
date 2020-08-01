
"""
This file continas webscrapers written for the purpose to source data
from different webpages to populate the iuppiter database.

author: Thomas Sontag
email: thomas.sontag@iuppiter-energie.de

Copyright 2020 iuppiter

"""

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from datetime import datetime
from sqlalchemy import create_engine
import json
import csv
import time
# import numpy as np
import pandas as pd
# import gc

from helper_functions import validate_zipcode, validate_consumption

import pprint as pp


# Global varibales

dt_out_format = "%Y-%m-%dT%H:%M:%SZ"  # ISO 8601

# url for AWS DB

# with open('aws_password.txt') as f:
#    fileReader = csv.reader(f)
#    for row in fileReader:
#        pw = ''.join(row)

pw = '=>Y5QEIDzQ%i:R{LN[AQ0]LB&'

cred = {
    'host': 'iuppiter-dev.ccovkmh788rj.eu-central-1.rds.amazonaws.com:5432',
    'db_name': 'iuppiter-dev',
    'user': 'thomas',
    'password': pw
}

db_url = 'postgresql://{0}:{1}@{2}/{3}'.format(cred['user'],
                                               cred['password'],
                                               cred['host'],
                                               cred['db_name'])

# url for logal postgres instance, for debugging and development

cred = {
    'host': 'localhost',
    'db_name': 'iuppiter_dev',
    'user': 'thomas',
    'password': '1234'
}

db_url_local = 'postgresql://{0}:{1}@{2}/{3}'.format(cred['user'],
                                                     cred['password'],
                                                     cred['host'],
                                                     cred['db_name'])

# Functions


def get_historical_dayahead_futures_eex(start_date, end_date, ENV='dev'):
    """
    Scrapes the historical power dayahead futures either the
    hourly average or the daily average and saves them into a postgres DB.
    If ENV is set to 'dev' the local postgres is used. Else the AWS
    postgres DB is used.
    """

    driver = webdriver.Firefox()

    # start_date = datetime(2020, 4, 1).date()

    dates = pd.date_range(start_date, end_date, freq='D')
    dates = list(dates.strftime('%Y/%m/%d'))
    dates.reverse()

    for date in dates:
        print(date)
        url = 'https://www.eex.com/de/marktdaten/strom/strom-indizes/auktion#!/{0}'.format(date)
        # url = 'https://www.eex.com/en/market-data/power/power-indices/auction#!/{0}'.format(date)
        print(url)

        result = []

        driver.get(url)
        time.sleep(0.5)  # wait until page is fully loaded

        driver.refresh()
        time.sleep(1.5)

        hours_elem = driver.find_elements_by_class_name('ng-scope')
        raw_data = hours_elem[1].get_attribute('textContent').split()[13:]

        periods = raw_data[::2]

        prices = raw_data[1::2]
        for i in range(0, len(prices)):
            prices[i] = prices[i].replace(',', '.')

        assert len(prices) == len(periods)
        dates = [date]*len(prices)

        result.append(list(zip(dates, periods, prices)))

        data = [j for i in result for j in i]

        if ENV == 'dev':
            engine = create_engine(db_url)

        else:
            engine = create_engine(db_url)

        columns = ['date', 'period', 'price']

        df = pd.DataFrame(data, columns=columns)
        df["date"] = df["date"].apply(pd.to_datetime)
        df["price"] = df["price"].apply(pd.to_numeric)
        tablename = 'eex_historical_power_dayahead_futures_hourly'

        df.to_sql(tablename, con=engine, if_exists='append', index=False)

        print(df.size)

    driver.quit()  # Close browser

    # print(result)
    # data = [j for i in result for j in i]
    # columns = ['Date', 'Period (CET)', 'Price in EUR/MWh ']
    # df = pd.DataFrame(data, columns=columns)

    # dt_of_query = datetime.utcnow().strftime(dt_out_format)

    # Write dataframe to postgres DB #########################

    # dbConnection = engine.connect()

    # df = pd.read_sql("select * from \"exx_historical_power_dayahead_futures_daily\"", dbConnection)

    # dbConnection.close()

    # df.to_csv('{0}_historical_dayahead_futures.csv'.format(dt_of_query),
    #          sep=',', header=columns, date_format='%Y/%m/%d', index=False,
    #          encoding='utf-8', float_format="%.2f")


def get_power_futures_exx():

    url = 'https://www.eex.com/en/market-data/power/futures#%7B%22snippetpicker%22%3A%22EEX%20German%20Power%20Future%22%7D'
    print("scraping: ", url)

    driver = webdriver.Firefox()
    driver.get(url)

    query_dt = datetime.utcnow()
    timestamp = query_dt.strftime(dt_out_format)
    driver.find_elements_by_class_name('uo_cookie_btn_type_1')[0].click()
    time.sleep(3)
    period_buttons = driver.find_elements_by_xpath("//*[contains(@class,'mv-button-base mv-hyperlink-button')]")


    time.sleep(2)

    #product_elem = driver.find_element_by_class_name('gradient-red')
    #product_name = '_'.join(product_elem.get_attribute('textContent').split())

    header = driver.find_element_by_class_name(
        'mv-quote-header-row').get_attribute('textContent').split()

    header.insert(0, 'Timestamp')
    header.insert(1, 'Period')
    header.insert(2, 'Type')
    header = tuple(header)

    data = []
    dates = []
    for period_button in period_buttons:
        period_button.click()
        time.sleep(2)

        period = period_button.get_attribute('textContent')

        if period:
            rows = driver.find_elements_by_class_name('mv-quote-row')

            row_content = [row.text.split() for row in rows]

            for row in row_content:

                if period != 'Week' and period != 'Weekend':

                    row.insert(0, period)

                    if row[1] not in dates:
                        dates.append(row[1])
                        row.insert(1, 'Baseload')
                        row.insert(0, timestamp)

                    else:
                        row.insert(1, 'Peakload')
                        row.insert(0, timestamp)
                    data.append(tuple(row))

    # file_name = '_'.join(
    #    (product_name, query_dt.strftime(dt_out_format), '.csv'))
    # print('output: ',  file_name)

    engine = create_engine(db_url)

    columns = [
        'query', 'period', 'type', 'name', 'last_price',
        'last_volume', 'settlement_price', 'volume_exchange',
        'volume_trade_registration', 'open_interest'
    ]

    df = pd.DataFrame(data, columns=columns)

    df["query"] = df["query"].apply(pd.to_datetime)

    tablename = 'eex_power_futures'

    df.to_sql(tablename, con=engine, if_exists='append', index=False)

    print(df.size)
    return df

    driver.quit()  # Close browser


def get_end_customer_rates_verivox(zipcode, consumption, csv=False):
    url = 'https://www.verivox.de/gewerbestrom/'

    validate_zipcode(zipcode)
    validate_consumption(consumption)

    driver = webdriver.Firefox()
    driver.get(url)

    time.sleep(2)
    return None


def get_end_customer_rates_check24(zipcode, consumption, csv=False):
    """
        Scrapes Data from the check24 website.
     Returns the end customer rates associated with each
     electricity tariff on check24 as pandas dataframe. saves it into a
     csv file if csv=True,
     takes as input the zipcode and annual consumption in kWh as string

    """

    validate_zipcode(zipcode)
    validate_consumption(consumption)

    url = 'https://www.check24.de/strom/'

    driver = webdriver.Firefox()
    driver.get(url)

    time.sleep(2)

#    try:
#        cookie_button = driver.find_element_by_class_name(
#            'c24-cookie-button')

#        cookie_button.click()

#    except ElementNotInteractableException:
#        pass

    zipcode_input = driver.find_element_by_id('c24api_zipcode')
    zipcode_input.clear()
    zipcode_input.send_keys(zipcode)

    consumption_input = driver.find_element_by_id('c24api_totalconsumption')
    consumption_input.clear()
    consumption_input.send_keys(consumption)

    compare_button = driver.find_element_by_id('c24_calculate')
    compare_button.click()

    query_dt = datetime.utcnow()

    time.sleep(9)  # Wait until all results are loaded and pop up disappears

    # scoll down to the bottom of the page  and load additional results,
    # until every result is visible
    try:
        while True:
            driver.execute_script("window.scrollTo(0, \
             document.body.scrollHeight);")

            load_add_res = driver.find_element_by_class_name(
                'paginator__button')

            load_add_res.click()
            time.sleep(2)

    except ElementNotInteractableException:
        pass

    finally:
        driver.refresh()
        provider_price_details = driver.find_elements_by_class_name(
            'ajax-pricelayer')

        data = [provider.get_attribute('textContent').split()
                for provider in provider_price_details]

        driver.quit()  # Close browser

        # Initialize dataframe
        columns = [
            'query', 'source', 'source_url', 'product_type',
            'consumption_type', 'zipcode', 'city', 'consumption',
            'max_contract_duration', 'applies_frm', 'hourly_rates',
            'basic_rates', 'immediate_bonus', 'new_customer_bonus'
        ]

        df = pd.DataFrame(columns=columns)

        # Process Data and append to dataframe
        print(data)
        df['hourly_rates'] = [
            float(e[e.index('Arbeitspreis') + 5].replace(',', '.'))
            if 'Arbeitspreis' in e else None for e in data
        ]

        df['basic_rates'] = [
            float(e[e.index('Grundpreis') + 3].replace(',', '.'))
            if 'Grundpreis' in e else None for e in data
        ]

        df['applies_frm'] = [
            (datetime.strptime(e[e.index('gultig')+2],
                               '%d.%m.%Y.').date()).strftime('%Y-%m-%d')
            if 'gultig' in e else None for e in data
        ]

        df['immediate_bonus'] = [
            float(e[e.index('Sofortbonus')+1].replace(',', '.'))
            if 'Sofortbonus' in e else None for e in data
        ]

        df['new_customer_bonus'] = [
            float(e[e.index('Neukundenbonus')+1].replace(',', '.'))
            if 'Neukundenbonus' in e else None for e in data
        ]

        df['city'] = [data[1][5]]*len(data)
        df['source'] = ['check24']*len(data)
        df['source_url'] = [url]*len(data)
        df['product_type'] = ['power']*len(data)
        df['consumption_type'] = ['H0']*len(data)
        df['max_contract_duration'] = [12]*len(data)
        df['query'] = [query_dt.strftime(dt_out_format)]*len(data)
        df['zipcode'] = [int(zipcode)]*len(data)
        df['consumption'] = [int(consumption)]*len(data)

        # print(df)

        engine = create_engine(db_url)

        tablename = 'end_customer_rates_power'

        df.to_sql(tablename, con=engine, if_exists='append', index=False)

        if csv:
            df.to_csv('{0}_{1}_H0_{2}.csv'.format(
                zipcode, df['city'][0], consumption
            ),
                sep=',', header=columns, date_format=dt_out_format,
                index=False, encoding='utf-8', float_format="%.2f")

        return df.to_json(orient='records')


if __name__ == "__main__":

    # pp = pprint.PrettyPrinter(indent=4)

    # requested_reports = [('49090', '2500'), ('50937', '2500'),
    #                     ('10115', '2500'), ('20095', '2500'),
    #                     ('80333', '2500')]

    # requested_reports = [(('49090', '2500'))]

    # print(get_historical_dayahead_futures_eex())

    # print(get_power_futures_exx())
    zipcode, consumption = 49090, 2500

    start_date, end_date = '2020-05-08', '2020-05-22'

    ENV = 'prod'

    #print(get_historical_dayahead_futures_eex(start_date, end_date, ENV))

    #pp.pprint(get_power_futures_exx())
    #pp.pprint(get_end_customer_rates_check24(zipcode, consumption))

    pp.pprint(json.loads(get_end_customer_rates_check24(zipcode, consumption)))
