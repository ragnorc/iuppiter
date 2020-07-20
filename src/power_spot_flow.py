from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
import pandas as pd
import json
import datetime
import matplotlib.pyplot as plt
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import requests
import xmltodict



def fetch_daily_spot():
    res = requests.get("https://transparency.entsoe.eu/api?documentType=A44&securityToken=dcce50af-fffe-43ee-b8b8-b2a0bdc35d6f&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H", params={'periodStart': (datetime.datetime.today()- datetime.timedelta(days=2)).strftime("%Y%m%d")+"2200", 'periodEnd': (datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%Y%m%d")+"2200"})
    print(str([ point["price.amount"]  for point in xmltodict.parse(res.content)["Publication_MarketDocument"]["TimeSeries"]["Period"]["Point"]]))


def fetch_historical_spot():
    client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
    df = pd.DataFrame(client.query(q.map_expr(
    lambda x: {"ds": q.select(["data","datetime"],q.get(x)), "y": q.select(["data","price"],q.get(x))},
        q.paginate(q.documents(q.collection('PowerSpot')), size=100000)
        ))["data"])
    df["ds"] = pd.to_datetime(df['ds'])
    return df


def train_prophet(historical_spot):
    print("hello local")
    model = Prophet(daily_seasonality=True)
    model.add_country_holidays(country_name='DE')
    print(historical_spot)
    return model.fit(historical_spot)


def predict_spot(model, future):
    forecast = model.predict(future)
    fig = model.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), model, forecast)
    #plt.show()
    return forecast

def write_to_db(items, collection, index, unique_key):
    def chunk(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
    for items in chunk(items, 500):
        print(len(items))
        client.query(
    q.map_expr(
        lambda item:
       q.call(
    q.function('upsert'),
    [collection,index, q.select(unique_key, item), item ],
  ),
      items
        )
    )



fetch_daily_spot()
historical_spot = fetch_historical_spot()
trained_model = train_prophet(historical_spot)
forecast = predict_spot(trained_model, pd.date_range(start=(historical_spot["ds"]).max(), end=historical_spot["ds"].max()+pd.offsets.DateOffset(years=6), freq="H").to_frame(index=False, name='ds'))
print(forecast)
write_to_db([{"datetime": item['ds'].replace('Z', ''), "price": item['yhat'], **item} for item in json.loads(forecast.to_json(orient='records', date_format="iso"))], "PowerSpotForecast","power_spot_forecast_datetime", "datetime")
