from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
import pandas as pd 
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import matplotlib.pyplot as plt

client = FaunaClient(secret="fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO")
df = pd.DataFrame(client.query(q.map_expr(
    lambda x: {"ds": q.select(["data","datetime"],q.get(x)), "y": q.select(["data","price"],q.get(x))},
        q.paginate(q.documents(q.collection('PowerSpot')), size=100000)
        ))["data"])
df["ds"] = pd.to_datetime(df['ds'])

model = Prophet(daily_seasonality=True)
model.add_country_holidays(country_name='DE')
model.fit(df)
#forecast = model.predict(start=pd.date_range(start=df["ds"].max(), end=df["ds"].max()+pd.offsets.DateOffset(days=10), freq="H").to_frame(index=False, name='ds'))
forecast = model.predict(pd.date_range(start="2020-07-13", end="2020-07-20", freq="H").to_frame(index=False, name='ds'))
print(forecast[["ds","weekly", "yhat", "daily"]])
print(model.plot_components(forecast))
plt.show()
