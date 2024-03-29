import pandas as pd
import json
import datetime
import matplotlib.pyplot as plt
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import requests
import math
from utils import write_to_db
from dateutil import tz



def fetch_eex_futures(product, type, date):
    data = requests.get("https://wrapapi.com/use/ragnorc/eex/futures/latest", params={"wrapAPIKey": "Vw52prEVYvxTYP7JN9MpNCIDVOKvf2iI", "product": '"/E.DE{}{}"'.format(type[0].upper(), product[0].upper()), "expirationDate": date.strftime("%Y/%m/%d"), "onDate": date.strftime("%Y/%m/%d")}).json()["data"]["output"]
    results = []
    for x in data:
        if x["close"]:

            result = {
        "date": date.date().isoformat(),
        #"closePrice": x["close"],
        "displayDate": datetime.datetime.strptime(x["gv.displaydate"], '%m/%d/%Y').date().isoformat(),
        "product": product,
        "year": datetime.datetime.strptime(x["gv.displaydate"], '%m/%d/%Y').year,
        "quarter": int(math.ceil(datetime.datetime.strptime(x["gv.displaydate"], '%m/%d/%Y').month/3)) if product !="year" else None,
        "month": datetime.datetime.strptime(x["gv.displaydate"], '%m/%d/%Y').month if product=="month" else None,
        
         
    } 
            result[type] = x["close"]
            result["original_"+type] = x
        
            results.append(result)
    return results


for product in ["month", "quarter", "year"]:
    for type in {"base", "peak"}:
        data = fetch_eex_futures(product, type, datetime.datetime.today() - datetime.timedelta(2))
        print(data)
        write_to_db(data, "PowerFutures", "power_futures_unique", ["date", "product", "displayDate"])
