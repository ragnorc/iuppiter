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
import os
from tasks import write_to_db

def fetch_historical_spot():
    client = FaunaClient(secret=os.environ["FAUNA_SECRET"])
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

historical_spot = fetch_historical_spot()
trained_model = train_prophet(historical_spot)
forecast = predict_spot(trained_model, pd.date_range(start=(historical_spot["ds"]).max(), end=historical_spot["ds"].max()+pd.offsets.DateOffset(years=6), freq="H").to_frame(index=False, name='ds'))
print(forecast)
write_to_db([{**item, "datetime": item['ds'].replace('Z', ''), "price": item['yhat'] } for item in json.loads(forecast.to_json(orient='records', date_format="iso"))], "PowerSpotForecast","power_spot_forecast_datetime", "datetime")
