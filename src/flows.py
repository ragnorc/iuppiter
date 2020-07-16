import prefect
from prefect import task, Flow
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




@task
def fetch_daily_spot():
    res = requests.get("https://transparency.entsoe.eu/api?documentType=A44&securityToken=dcce50af-fffe-43ee-b8b8-b2a0bdc35d6f&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H", params={'periodStart': (datetime.datetime.today()- datetime.timedelta(days=2)).strftime("%Y%m%d")+"2200", 'periodEnd': (datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%Y%m%d")+"2200"})
    logger = prefect.context.get("logger")
    logger.info("An info message.")
    logger.warning("A warning message.")
    logger.info(str([ point["price.amount"]  for point in xmltodict.parse(res.content)["Publication_MarketDocument"]["TimeSeries"]["Period"]["Point"]]))

@task
def fetch_historical_spot():
    client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
    df = pd.DataFrame(client.query(q.map_expr(
    lambda x: {"ds": q.select(["data","datetime"],q.get(x)), "y": q.select(["data","price"],q.get(x))},
        q.paginate(q.documents(q.collection('PowerSpot')), size=100000)
        ))["data"])
    df["ds"] = pd.to_datetime(df['ds'])
    return df

@task()
def train_prophet(historical_spot):
    print("hello local")
    model = Prophet(daily_seasonality=True)
    model.add_country_holidays(country_name='DE')
    print(historical_spot)
    return model.fit(historical_spot)

@task()
def predict_spot(model, historical_spot, years):
    future = pd.date_range(start=(historical_spot["ds"]).max(), end=historical_spot["ds"].max()+pd.offsets.DateOffset(years=years), freq="H").to_frame(index=False, name='ds')
    forecast = model.predict(future)
    fig = model.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), model, forecast)
    plt.show()
    return forecast

@task
def write_to_db(items, fn, collection, index, unique_key):
    def chunk(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
    items = [fn(item) for item in json.loads(items.to_json(orient='records', date_format="iso"))]
    for items in chunk(items, 500):
        prefect.context.get("logger").info(str(items))
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


with Flow('Fetch Daily Power Spot Flow') as fetch_daily_power_spot_flow:
    fetch_daily_spot()


with Flow('Spot Flow') as spot_flow:
    historical_spot = fetch_historical_spot()
    trained_model = train_prophet(historical_spot)
    forecast = predict_spot(trained_model, historical_spot, 6)
    write_to_db(forecast, lambda item: {"datetime": item['ds'].replace('Z', ''), "price": item['yhat'], **item}, "PowerSpotForecast","power_spot_forecast_datetime", "datetime")
