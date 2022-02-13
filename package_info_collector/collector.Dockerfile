# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM docker:20.10.12-alpine3.15

# copy crontabs for root user
COPY cronjobs /etc/crontabs/root

ADD . /collector
WORKDIR /collector

# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]