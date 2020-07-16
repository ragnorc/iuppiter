import prefect
from prefect import task, Flow

import requests 
import xmltodict

@task
def fetch_daily_spot():
    res = requests.get("https://transparency.entsoe.eu/api?documentType=A44&securityToken=dcce50af-fffe-43ee-b8b8-b2a0bdc35d6f&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H", params={'periodStart': (datetime.datetime.today()- datetime.timedelta(days=2)).strftime("%Y%m%d")+"2200", 'periodEnd': (datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%Y%m%d")+"2200"})
    logger = prefect.context.get("logger")
    logger.info("An info message.")
    logger.warning("A warning message.")
    logger.info(str([ point["price.amount"]  for point in xmltodict.parse(res.content)["Publication_MarketDocument"]["TimeSeries"]["Period"]["Point"]]))


with Flow('Fetch Daily Power Spot Flow') as fetch_daily_power_spot_flow:
    fetch_daily_spot()
