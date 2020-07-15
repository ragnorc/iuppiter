FROM prefecthq/prefect:0.12.2-python3.6

# install some base utilities
RUN apt update && apt install build-essential -y build-essential && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install curl -y


# Mono: 5.20

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
  && echo "deb http://download.mono-project.com/repo/debian stretch/snapshots/5.20 main" > /etc/apt/sources.list.d/mono-official.list \
  && apt-get update \
  && apt-get install -y clang \
  && apt-get install -y mono-devel=5.20\* \
  && rm -rf /var/lib/apt/lists/* /tmp/*

RUN pip install --upgrade setuptools

RUN pip install pycparser \
  && pip install pythonnet \
  && pip install numpy \
  && pip install pandas \
  && pip install matplotlib \
  && pip install curves \
  && pip install faunadb \
  && pip install xmltodict

RUN pip install 'pystan>=2.19.0, <3.0.0'
RUN pip install 'holidays==0.9.12'
RUN pip install 'fbprophet<0.6'
RUN pip install 'PyGithub'

COPY src/ /src/
#ENV PREFECT__CLOUD__AGENT__AUTH_TOKEN=RgvvYs31p8KiKB2iFXfR8g
ENTRYPOINT [ "prefect", "agent", "start", "local", "-t" ,"tpqKLNNyqrwjSFjK4KAypQ" ]
#ENTRYPOINT [ "python", "/src/main.py" ]

# Pythonnet: 2.5.0 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built
