FROM debian:10

RUN sed -i 's/^deb.*/&\n@&/' /etc/apt/sources.list
RUN sed -i 's/@deb/deb-src/g' /etc/apt/sources.list

RUN apt update
RUN apt install -y python3-pip

WORKDIR /collector
COPY requirements.txt /collector
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY collector.py /collector

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "collector.py"]
