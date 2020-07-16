import os


import prefect
from prefect import task, Flow
from prefect.environments.storage import GitHub
from prefect.agent import Agent
from power_spot_flow import power_spot_flow


power_spot_flow.storage = GitHub(repo="ragnorc/iuppiter", path="src/power_spot_flow.py")

#storage.add_flow(spot_flow)
#storage.add_flow(fetch_daily_power_spot_flow)
#storage = storage.build()

#spot_flow.storage = storage
#fetch_daily_power_spot_flow.storage = storage
#print(storage.flows)
print("Registering flows...")
power_spot_flow.register(project_name="iuppiter", build=True)
power_spot_flow.run()
