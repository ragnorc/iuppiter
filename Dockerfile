FROM ubuntu:bionic

# Install some base utilities
RUN apt update && apt install build-essential -y build-essential gnupg ca-certificates && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y wget curl unzip \
   fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 libgbm1


RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# install geckodriver and firefox

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP


# install chromedriver and google-chrome

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN CHROME_SETUP=google-chrome.deb && \
    wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" && \
    dpkg -i $CHROME_SETUP && \
    apt-get install -y -f && \
    rm $CHROME_SETUP


# Mono

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
&& echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" > /etc/apt/sources.list.d/mono-stable.list \
  && apt-get update \
  && apt-get install -y clang \
  && apt-get install -y mono-devel \
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
RUN pip install 'selenium-wire'


#ENV PREFECT__CLOUD__AGENT__AUTH_TOKEN=tpqKLNNyqrwjSFjK4KAyp

#ENTRYPOINT [ "prefetc", "agent", "start", "local", "-t", "tpqKLNNyqrwjSFjK4KAyp" ]
#ENTRYPOINT ["sh", "-c", "prefect agent start local -t $PREFECT__CLOUD__AGENT__AUTH_TOKEN"]
#ENTRYPOINT [ "python", "/src/main.py" ]

# Pythonnet: 2.5.0 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built
