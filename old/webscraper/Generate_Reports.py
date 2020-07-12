from selenium import webdriver
from time import sleep
from datetime import datetime

#import sqlite3
import re
import os
import pprint
import matplotlib.pyplot as plt
import numpy as np

dt_out_format = "%Y-%m-%dT%H:%M:%SZ" # ISO 8061

def get_data_eex():

    url = 'https://www.eex.com/en/market-data/power/futures/phelix-de-futures'

    driver = webdriver.Firefox()
    driver.get(url)

    query_dt = datetime.utcnow()
    timestamp = query_dt.strftime(dt_out_format)

    period_buttons = driver.find_elements_by_class_name('mv-button-base')

    sleep(5)

    product = driver.find_element_by_class_name('gradient-red').get_attribute('textContent').split()
    print(product)

    header  = driver.find_element_by_class_name('mv-quote-header-row').get_attribute('textContent').split()
    header.insert(0,'Timestamp')
    header.insert(1,'Period')
    header.insert(2,'Type')
    header = tuple(header)

    print(header)

    data = []
    dates = []
    for period_button in period_buttons:
        period_button.click()
        sleep(0.5)

        period = period_button.get_attribute('textContent')

        if period:
            rows = driver.find_elements_by_class_name('mv-quote-row')
            row_content = [row.text.split() for row in rows]

            for row in row_content:

                if period != 'Week' and period != 'Weekend':

                    row.insert(0,period)

                    if row[1] not in dates:
                        dates.append(row[1])
                        row.insert(1,'Baseload')
                        row.insert(0,timestamp)
                    else:
                        row.insert(1,'Peakload')
                        row.insert(0,timestamp)
                    data.append(tuple(row))


    #print(data)
    #timestamps = [query_dt.strftime(dt_out_format)]*len(data)
    #timestamps.insert(0, "Zeitstempel")

    #print('Dates:',dates)

    #print(header)
    print(data)

    file_name = '_'.join(product) + '_' + query_dt.strftime(dt_out_format) + '_' +  ".csv"

    np.savetxt(file_name, data, delimiter = ';', header = 'Timestamp; Period; Type; Name; Last Price; Last Volume; Settlement Price; Volume Exchange; Volume Trade Registration; Open Interest'  , fmt='%s') # expects [(...),(...),...]

    driver.quit() ## Close browser

def get_data_check24(zipcode, consumption):
    '''Returns the end customer rates associated with each electricity tariff on check24 and saves it into a csv file, takes as input the zipcode and annual consumption in kWh'''

    assert isinstance(zipcode, str)
    assert re.match(r"([0]{1}[1-9]{1}|[1-9]{1}[0-9]{1})[0-9]{3}",zipcode) # cheks if zipcode is valid
    assert len(zipcode) == 5 # zipcodes in Germany have exactly 5 digits

    assert isinstance(consumption, str)
    assert int(consumption) >= 100 # mim consumption that is required by check24, otherwise an error will occur

    url = 'https://www.check24.de/strom/'

    driver = webdriver.Firefox()
    driver.get(url)

    sleep(1)
    cookie_button = driver.find_element_by_class_name('c24-cookie-button')
    cookie_button.click()

    zipcode_input = driver.find_element_by_id('c24api_zipcode')
    zipcode_input.clear()
    zipcode_input.send_keys(zipcode)

    consumption_input = driver.find_element_by_id('c24api_totalconsumption')
    consumption_input.clear()
    consumption_input.send_keys(consumption)

    compare_button = driver.find_element_by_id('c24_calculate')
    compare_button.click()

    query_dt = datetime.utcnow()

    sleep(9) # Wait until all results are loaded abd pop up disappears

    try:
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            load_additional_results = driver.find_element_by_class_name('paginator__button')
            load_additional_results.click()
            sleep(2)
    finally:
        driver.refresh()
        provider_price_details = driver.find_elements_by_class_name('ajax-pricelayer')

        data =  [provider.get_attribute('textContent').split() for provider in provider_price_details]

        #data = {brand.get_attribute('alt'): price_details.get_attribute('textContent').split() for (brand,price_details) in list(zip(brands,provider_price_details))}
        #print(data)

        driver.quit() ## Close browser

        ###### Process Data and store in csv #####

        city = [e[5] for e in data]
        city.insert(0, "Stadt")
        #print(city)

        hourly_rates = [e[e.index('Arbeitspreis') + 3] if 'Arbeitspreis' in e else '-' for e in data ]
        hourly_rates.insert(0, "Arbeitspreis [Ct./kWh]")
        #print(hourly_rates)

        basic_rates = [e[e.index('Grundpreis') + 1] if 'Grundpreis' in e else '-' for e in data]
        basic_rates.insert(0, "Grundpreis in [EUR/Jahr] ")
        #print(basic_rates)

        #total_rate_without_bonus = [e[e.index('Gesamtpreis')+3] if 'Gesamtpreis' in e else '-' for e in data]
        #total_rate_without_bonus.insert(0, "Gesamtpreis ohne Bonus [EUR/Jahr] ")
        #print(total_rate_without_bonus)

        applies_frm = [e[e.index('gültig')+2] if 'gültig' in e else '-' for e in data]
        applies_frm.insert(0, "Angebot gilt ab")
        for date in applies_frm:
            date
        #print(applies_frm)

        immediate_bonus = [e[e.index('Sofortbonus')+1] if 'Sofortbonus' in e else '-' for e in data ]
        immediate_bonus.insert(0, "Sofortbonus in EUR")
        #print(immediate_bonus)

        new_customer_bonus = [e[e.index('Neukundenbonus')+1] if 'Neukundenbonus' in e else '-' for e in data ]
        new_customer_bonus.insert(0, "Neukundenbonus in EUR")
        #print(new_customer_bonus)

        source = ['check24']*len(data)
        source.insert(0, "Quelle")
        #print(source)

        timestamps = [query_dt.strftime(dt_out_format)]*len(data)
        timestamps.insert(0, "Zeitstempel")
        #print(timestamps)

        zipcodes = [zipcode]*len(data)
        zipcodes.insert(0, "PLZ")
        #print(zipcodes)

        consumptions = [consumption]*len(data)
        consumptions.insert(0, "Verbrauch [kWh/Jahr]")
        #print(consumptions)

        #dir = "/Documents/iuppiter/Code/iuppiter/python-impl⁩/"
        file_name = zipcode + '_' + city[1] + '_' + 'H0' + '_' + consumption + ".csv"
        #complete_path = os.path.join(dir,file_name+".csv")
        np.savetxt(file_name, [p for p in zip(timestamps, source, zipcodes, city, consumptions, applies_frm, hourly_rates,basic_rates, immediate_bonus, new_customer_bonus)], delimiter=';', fmt='%s', encoding = 'utf-8' )

        return query_dt.strftime(dt_out_format),len(data)

def plot_price_distribution(hourly_rates):
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    # Remove the plot frame lines. They are unnecessary chartjunk.
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Along the same vein, make sure your axis labels are large
    # enough to be easily read as well. Make them slightly larger
    # than your axis tick labels so they stand out.
    plt.xlabel("Elo Rating", fontsize=16)
    plt.ylabel("Count", fontsize=16)

    # Plot the histogram. Note that all I'm passing here is a list of numbers.
    # matplotlib automatically counts and bins the frequencies for us.
    # "#3F5D7D" is the nice dark blue color.
    # Make sure the data is sorted into enough bins so you can see the distribution.
    plt.hist(list(hourly_rates),
         color="#3F5D7D", bins=100)

    # Always include your data source(s) and copyright notice! And for your
    # data sources, tell your viewers exactly where the data came from,
    # preferably with a direct link to the data. Just telling your viewers
    # that you used data from the "U.S. Census Bureau" is completely useless:
    # the U.S. Census Bureau provides all kinds of data, so how are your
    # viewers supposed to know which data set you used?
    plt.text(1300, -5000, "Data source: www.ChessGames.com | "
         "Author: Randy Olson (randalolson.com / @randal_olson)", fontsize=10)

    # Finally, save the figure as a PNG.
    # You can also save it as a PDF, JPEG, etc.
    # Just change the file extension in this call.
    # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.
    plt.savefig("chess-elo-rating-distribution.png", bbox_inches="tight");

    plt.show()

if __name__ == "__main__":
    os.chdir('/Users/thomas/Documents/iuppiter/Code/iuppiter/python-impl/')
    #pp = pprint.PrettyPrinter(indent=4)
    #print('current working dir:',os.getcwd())

    #conn = sqlite3.connect('reports_data.db')
    #c = conn.cursor()
    #try:
    #    c.execute(""" CREATE TABLE end_customer_prices (Zeitstempel text) """)
    #    conn.commit()
    #finally:
    #    conn.close()

    requested_reports = [('49090','2500'),('50937','2500'),('10115','2500'),('20095','2500'),('80333','2500')]

    print(get_data_eex())

    #for zipcode, consumption in requested_reports:
        #get_data_check24(zipcode, consumption)
