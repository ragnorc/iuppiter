import pandas as pd 
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import json
import numpy as np

def chunk(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


df = pd.read_csv('spot.csv')
df['time'] = (df['date'].str[0:10] + " " + df['period'].str[0:2] + ":00:00")
df['time'] = df["time"].astype("datetime64")
df["time"] = df["time"]
df['price'] = df['price']
df.to_csv("spotutc.csv", index=False)
print(type(json.loads(df.iloc[0:5].to_json(orient='records'))))

client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")


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
