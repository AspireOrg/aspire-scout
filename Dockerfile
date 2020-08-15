FROM aspireorg/federatednode

MAINTAINER Aspire Developers <admin@aspirecrypto.com>

# Install SASS
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.1/install.sh | bash \
	&& . ~/.nvm/nvm.sh \
	&& nvm install v13.6.0 \
	&& npm install -g sass

# Install deps
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev software-properties-common git lib32ncurses5-dev pkg-config curl
RUN add-apt-repository ppa:deadsnakes/ppa
RUN add-apt-repository ppa:tah83/secp256k1
RUN apt-get update
RUN apt-get install -y libsecp256k1-dev

# Install
COPY . /scout
WORKDIR /scout
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.5 get-pip.py
RUN pip3.5 install wheel
RUN pip3.5 install -r requirements.txt

COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod a+x /usr/local/bin/start.sh

EXPOSE 8182
EXPOSE 8183

ENTRYPOINT ["start.sh"]
