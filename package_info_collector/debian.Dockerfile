# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM debian:10

RUN sed -i 's/^deb.*/&\n@&/' /etc/apt/sources.list
RUN sed -i 's/@deb/deb-src/g' /etc/apt/sources.list

RUN apt update
RUN apt install -y python3-pip

WORKDIR /collector
COPY requirements.txt /collector
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY apt_collector.py /collector

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "apt_collector.py"]
