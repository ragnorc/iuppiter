import schedule
import time
import json
import pprint

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from webscraper import get_end_customer_rates_check24

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)

# set environment with ENV variable
ENV = 'DEV'

if ENV == 'DEV':

    credentials = {
        'host': 'localhost',
        'database': 'iuppiter_dev',
        'user': 'thomas',
        'password': '1234'
    }

    uri = 'postgresql://{0}:{1}@{2}/{3}'.format(credentials['user'],
                                                credentials['password'],
                                                credentials['host'],
                                                credentials['database'],)

    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

else:

    with open('aws_password.txt') as f:
        pw = f.read()

    credentials = {
        'host': 'ccovkmh788rj.eu-central-1.rds.amazonaws.com:5432',
        'database': 'iuppiter-dev',
        'user': 'thomas',
        'password': pw
    }

    uri = 'postgresql://{0}:{1}@{2}/{3}'.format(credentials['user'],
                                                credentials['password'],
                                                credentials['host'],
                                                credentials['database'],)

    # uri = 'postgresql://thomas:password@iuppiter-dev.ccovkmh788rj.eu-central-1.rds.amazonaws.com:5432/iuppiter-dev'

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class RatesModel(db.Model):
    __tablename__ = 'end_customer_rates'

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.DateTime(timezone=True))
    source = db.Column(db.Text())
    source_url = db.Column(db.Text())
    product_type = db.Column(db.Text())
    consumption_type = db.Column(db.Text())
    zipcode = db.Column(db.Integer())
    city = db.Column(db.Text())
    consumption = db.Column(db.Integer())
    max_contract_duration = db.Column(db.Integer())
    # applies_frm = db.Column(db.Date())
    basic_rates = db.Column(db.Float())
    hourly_rates = db.Column(db.Float())
    immediate_bonus = db.Column(db.Float())
    new_customer_bonus = db.Column(db.Float())

    def __init__(self, query, source, source_url, product_type,
                 consumption_type, zipcode, city, consumption,
                 max_contract_duration, applies_frm, basic_rates,
                 hourly_rates, immediate_bonus, new_customer_bonus):

        self.query = query
        self.source = source
        self.source_url = source_url
        self.product_type = product_type
        self.consumption_type = consumption_type
        self.zipcode = zipcode
        self.city = city
        self.consumption = consumption
        self.max_contract_duration = max_contract_duration
        self.applies_frm = applies_frm
        self.basic_rates = basic_rates
        self.hourly_rates = hourly_rates
        self.immediate_bonus = immediate_bonus
        self.new_customer_bonus = new_customer_bonus


def job():
    consumption = 2500
    # consumption_type = 'H0'

    if ENV == 'DEV':

        with open('cities_dev.json') as f:
            cities = json.load(f)
    else:

        with open('cities.json') as f:
            cities = json.load(f)

    for city in cities:
        out = get_end_customer_rates_check24(cities[city], consumption)

        for data in json.loads(out):

            new_entry = RatesModel(
                query=data["query"],
                source=data["source"],
                source_url=data["source_url"],
                product_type=data["product_type"],
                consumption_type=data["consumption_type"],
                zipcode=data["zipcode"],
                city=data["city"],
                consumption=data["consumption"],
                max_contract_duration=data["max_contract_duration"],
                applies_frm=data['applies_frm'],
                basic_rates=data['basic_rates'],
                hourly_rates=data['hourly_rates'],
                immediate_bonus=data['immediate_bonus'],
                new_customer_bonus=data['new_customer_bonus']
            )

            db.session.add(new_entry)
            db.session.commit()


if __name__ == "__main__":

    job()


else:
    # schedule.every().day.at("15:00").do(job,'It is 01:00')
    schedule.every(1440).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)  # wait one minute
