import prefect
from prefect import task, Flow
from prefect.environments.storage import Docker
from spot_flow import spot_flow


storage = Docker(
                 #registry_url="008422115532.dkr.ecr.eu-west-2.amazonaws.com/iuppiter",
                 dockerfile="Dockerfile"
                 )

storage.add_flow(spot_flow)
storage = storage.build()

spot_flow.storage = storage
print(storage.flows)
spot_flow.register(project_name="iuppiter", build=False)

spot_flow.run()
