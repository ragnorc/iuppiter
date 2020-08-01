FROM python:3.6-slim-buster

# Install some base utilities
RUN apt update && apt install build-essential -y build-essential && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install wget curl chromium -y

#=========
# Firefox
#=========
ARG FIREFOX_VERSION=latest
RUN FIREFOX_DOWNLOAD_URL=$(if [ $FIREFOX_VERSION = "latest" ] || [ $FIREFOX_VERSION = "nightly-latest" ] || [ $FIREFOX_VERSION = "devedition-latest" ] || [ $FIREFOX_VERSION = "esr-latest" ]; then echo "https://download.mozilla.org/?product=firefox-$FIREFOX_VERSION-ssl&os=linux64&lang=en-US"; else echo "https://download-installer.cdn.mozilla.net/pub/firefox/releases/$FIREFOX_VERSION/linux-x86_64/en-US/firefox-$FIREFOX_VERSION.tar.bz2"; fi) \
  && apt-get update -qqy \
  && apt-get -qqy --no-install-recommends install firefox libavcodec-extra \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
  && wget --no-verbose -O /tmp/firefox.tar.bz2 $FIREFOX_DOWNLOAD_URL \
  && apt-get -y purge firefox \
  && rm -rf /opt/firefox \
  && tar -C /opt -xjf /tmp/firefox.tar.bz2 \
  && rm /tmp/firefox.tar.bz2 \
  && mv /opt/firefox /opt/firefox-$FIREFOX_VERSION \
  && ln -fs /opt/firefox-$FIREFOX_VERSION/firefox /usr/bin/firefox

#============
# GeckoDriver
#============
ARG GECKODRIVER_VERSION=latest
RUN GK_VERSION=$(if [ ${GECKODRIVER_VERSION:-latest} = "latest" ]; then echo "0.27.0"; else echo $GECKODRIVER_VERSION; fi) \
  && echo "Using GeckoDriver version: "$GK_VERSION \
  && wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GK_VERSION/geckodriver-v$GK_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GK_VERSION \
  && chmod 755 /opt/geckodriver-$GK_VERSION \
  && ln -fs /opt/geckodriver-$GK_VERSION /usr/bin/geckodriver

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
RUN pip install 'selenium'


#ENV PREFECT__CLOUD__AGENT__AUTH_TOKEN=tpqKLNNyqrwjSFjK4KAyp

#ENTRYPOINT [ "prefetc", "agent", "start", "local", "-t", "tpqKLNNyqrwjSFjK4KAyp" ]
#ENTRYPOINT ["sh", "-c", "prefect agent start local -t $PREFECT__CLOUD__AGENT__AUTH_TOKEN"]
#ENTRYPOINT [ "python", "/src/main.py" ]

# Pythonnet: 2.5.0 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built
