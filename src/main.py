import os


import prefect
from prefect import task, Flow
from prefect.environments.storage import GitHub
from prefect.agent import Agent
from flows import forecast_power_spot_flow
from fetch_daily_power_spot import fetch_daily_power_spot_flow


forecast_power_spot_flow.storage = GitHub(repo="ragnorc/iuppiter", path="src/flows.py")
fetch_daily_power_spot_flow.storage = GitHub(repo="ragnorc/iuppiter", path="src/fetch_daily_power_spot.py")
#storage.add_flow(spot_flow)
#storage.add_flow(fetch_daily_power_spot_flow)
#storage = storage.build()

#spot_flow.storage = storage
#fetch_daily_power_spot_flow.storage = storage
#print(storage.flows)
forecast_power_spot_flow.register(project_name="iuppiter", build=True)
fetch_daily_power_spot_flow.register(project_name="iuppiter", build=True)
print("ran docker")
