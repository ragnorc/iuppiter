import pandas as pd 
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import json
import numpy as np
from utils import write_to_db 
import os

def chunk(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def from_csv():
    df = pd.read_csv('spot.csv')
    df['time'] = (df['date'].str[0:10] + " " + df['period'].str[0:2] + ":00:00")
    df['time'] = df["time"].astype("datetime64")
    df["time"] = df["time"]
    df['price'] = df['price']
    df.to_csv("spotutc.csv", index=False)
    print(type(json.loads(df.iloc[0:5].to_json(orient='records'))))

    client = FaunaClient(secret=os.environ["FAUNA_SECRET"])


    for df in chunk(df, 5000):
        print(len(df))
        client.query(
    q.map_expr(
            lambda item:  q.call(
        q.function('upsert'),
        [ 'PowerSpot','power_spot_datetime',q.select("datetime", item),  item ],
    ),
        [ {"datetime": x["time"].replace('Z', ''), "price": x["price"]} for x in json.loads(df.to_json(orient='records', date_format="iso")) ]
            )
        )
for year in range(2010,2020):
    with open('../data/year_dayahead_'+str(year)+'.json') as json_file:
        data = json.load(json_file)
    prices = np.array(data[1]["values"])[:,1]
    dates = pd.date_range("01/01/"+str(year), "01/01/"+str((year+1)), freq="H", closed="left")
    df = pd.DataFrame()
    df["price"] = prices
    df["datetime"] = dates
    print(len(prices))
    write_to_db([{**item, "datetime": item['datetime'].replace('Z', '')} for item in json.loads(df.to_json(orient='records', date_format="iso"))], "PowerSpot","power_spot_datetime", "datetime")
