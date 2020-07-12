import prefect
from prefect import task, Flow
from fbprophet import Prophet
import pandas as pd
import json
import datetime
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient



@task(cache_for=datetime.timedelta(hours=1))
def train_prophet():
    logger = prefect.context.get("logger")
    logger.info("Hello, Cloud!")
    print("hello local")
    model = Prophet(daily_seasonality=True)
    model.add_country_holidays(country_name='DE')
    df = pd.read_csv('spot.csv')
    df['ds'] = (df['date'].str[0:10] + " " + df['period'].str[0:2] + ":00:00")
    df['y'] = df['price']
    return model.fit(df)

@task(cache_for=datetime.timedelta(hours=1))
def predict_spot(model, freq):
    return model.predict(pd.date_range(start=str(datetime.datetime.today()), end=str(datetime.datetime.today().year+6), freq=freq).to_frame(index=False, name='ds'))

@task
def write_to_db(forecast, collection):
    client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
    client.query(
    q.map_expr(
        lambda item:
        q.create(
          q.collection(collection),
          { "data": item },
        ),
        json.loads(forecast.iloc[0:5].to_json(orient='records'))
        )
    )

with Flow('Spot Flow') as spot_flow:
    trained_model = train_prophet()
    daily_forecast = predict_spot(trained_model, "D")
    hourly_forecast = predict_spot(trained_model, "H")
    write_to_db(hourly_forecast, "PowerSpotHourlyForecast")
