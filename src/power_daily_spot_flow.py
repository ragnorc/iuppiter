import pandas as pd
import json
import datetime
import matplotlib.pyplot as plt
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import requests
import xmltodict
import os
from utils import write_to_db
from dateutil import tz


def fetch_daily_spot(day):
    print("Fetching daily spot price")
    start = datetime.datetime(day.year, day.month, day.day)
    end = start + datetime.timedelta(1)
    start_utc = datetime.datetime(day.year, day.month, day.day, tzinfo=tz.gettz("Europe/Berlin")).astimezone(tz.tzutc())
    end_utc = start_utc + datetime.timedelta(1)
    res = requests.get("https://transparency.entsoe.eu/api?documentType=A44&securityToken=dcce50af-fffe-43ee-b8b8-b2a0bdc35d6f&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H", params={'periodStart': start_utc.strftime("%Y%m%d%H%M"), 'periodEnd': end_utc.strftime("%Y%m%d%H%M")})
    prices = [ point["price.amount"]  for point in xmltodict.parse(res.content)["Publication_MarketDocument"]["TimeSeries"]["Period"]["Point"]]
    dates = pd.date_range(start, end, freq="H", closed="left")
    df = pd.DataFrame()
    df["price"] = prices
    df["datetime"] = dates
    print(df)
    return df


daily_spot = fetch_daily_spot(datetime.datetime.today()-datetime.timedelta(days=1))
print(daily_spot)
write_to_db([{**item, "datetime": item['datetime'].replace('Z', '')} for item in json.loads(daily_spot.to_json(orient='records', date_format="iso"))], "PowerSpot","power_spot_datetime", ["datetime"])
