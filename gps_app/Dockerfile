FROM gliderlabs/alpine:3.7

WORKDIR /usr/share/gpsclientapp

COPY requirements.txt /usr/share/gpsclientapp

ENV PYTHONUNBUFFERED=1

RUN echo "**** Install Python ****" && \
    apk add --update-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** Install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN pip install -r requirements.txt

ADD oauth.py /usr/share/gpsclientapp/oauth.py
ADD gps_client_app.py /usr/share/gpsclientapp/gps_client_app.py
ADD gps_client_api.py /usr/share/gpsclientapp/gps_client_api.py
ADD msgparser.py /usr/share/gpsclientapp/msgparser.py
ADD scripts/gpsclientapp.sh /usr/share/gpsclientapp/gpsclientapp.sh
