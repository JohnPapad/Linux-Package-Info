FROM ubuntu:20.04

RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
RUN apt update
RUN apt install python3-pip -y
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'ray[default]' && \
    pip install --no-cache-dir swh.model[cli]


WORKDIR /collector
COPY collector.py /collector

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "collector.py"]
