import schedule
import time
import json

from webscraper import get_power_futures_exx, get_end_customer_rates_check24


def check24():
    with open('cities.json') as f:
        cities = json.load(f)

        consumption = 2500

        for city in cities:
            get_end_customer_rates_check24(cities[city], consumption)


schedule.every().day.at("17:12").do(get_power_futures_exx)

schedule.every().day.at("17:14").do(check24)

# schedule.every(10).seconds.do(job)
while True:
    schedule.run_pending()
    time.sleep(5)  # wait one minute
