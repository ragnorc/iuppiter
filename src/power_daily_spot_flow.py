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
from tasks import write_to_db


def fetch_daily_spot():
    print("Fetching daily spot price")
    res = requests.get("https://transparency.entsoe.eu/api?documentType=A44&securityToken=dcce50af-fffe-43ee-b8b8-b2a0bdc35d6f&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H", params={'periodStart': (datetime.datetime.today()- datetime.timedelta(days=2)).strftime("%Y%m%d")+"2200", 'periodEnd': (datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%Y%m%d")+"2200"})
    prices = [ point["price.amount"]  for point in xmltodict.parse(res.content)["Publication_MarketDocument"]["TimeSeries"]["Period"]["Point"]]
    dates = pd.date_range((datetime.datetime.today()- datetime.timedelta(days=2)).strftime("%Y%m%d"),(datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%Y%m%d"), freq="H", closed="left")
    df = pd.DataFrame()
    df["price"] = prices
    df["datetime"] = dates
    print(df)
    return df


daily_spot = fetch_daily_spot()
write_to_db([{**item, "datetime": item['datetime'].replace('Z', '')} for item in json.loads(daily_spot.to_json(orient='records', date_format="iso"))], "PowerSpot","power_spot_datetime", "datetime")
