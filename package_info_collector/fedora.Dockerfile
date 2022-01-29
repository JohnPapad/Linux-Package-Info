# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM fedora:34

RUN dnf install -y python3-pip
RUN dnf install -y redhat-lsb-core

WORKDIR /collector
COPY requirements.txt /collector
RUN pip3 install --user --no-cache-dir --upgrade pip && \
    pip3 install --user --no-cache-dir -r requirements.txt

COPY dnf_collector.py /collector

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "dnf_collector.py"]
