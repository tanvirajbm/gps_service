FROM gliderlabs/alpine:3.7

WORKDIR /usr/share/gpsserviceapp

COPY requirements.txt /usr/share/gpsserviceapp

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

ADD gps_service.py /usr/share/gpsserviceapp/gps_service.py
ADD data.log /usr/share/gpsserviceapp/data.log
ADD scripts/startup.sh /usr/share/gpsserviceapp/startup.sh