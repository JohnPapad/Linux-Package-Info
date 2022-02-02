#!/bin/bash

GITHUB_TOKEN="" # your github account token - fill it out
SHM_SIZE="5.07gb" # considering that your machine has 16 GB of RAM - change it accordingly otherwise
BACKEND_API="http://localhost:8000/api/v1" # considering that the backend runs on the same machine - change it accordingly otherwise
USERNAME="" # your credentials to login to backend API - fill it out
PASSWORD="" # your credentials to login to backend API - fill it out

# Ubuntu:
docker build -t ubuntu_distro -f ubuntu.Dockerfile .
docker run --net host --shm-size=$SHM_SIZE --env GITHUB-TOKEN=$GITHUB_TOKEN --env USERNAME=$USERNAME --env PASSWORD=$PASSWORD ubuntu_distro python3 apt_collector.py -d Ubuntu -u $BACKEND_API -a http://archive.ubuntu.com/ubuntu

# Debian:
docker build -t debian_distro -f debian.Dockerfile .
docker run --net host --shm-size=$SHM_SIZE --env GITHUB-TOKEN=$GITHUB_TOKEN --env USERNAME=$USERNAME --env PASSWORD=$PASSWORD debian_distro python3 apt_collector.py -d Debian -u $BACKEND_API -a http://ftp.debian.org/debian

# Kali:
docker build -t kali_distro -f kali.Dockerfile .
docker run --net host --shm-size=$SHM_SIZE --env GITHUB-TOKEN=$GITHUB_TOKEN --env USERNAME=$USERNAME --env PASSWORD=$PASSWORD kali_distro python3 apt_collector.py -d Kali -u $BACKEND_API -a https://http.kali.org

# Fedora:
docker build -t fedora_distro -f fedora.Dockerfile .
docker run --net host --shm-size=$SHM_SIZE --env GITHUB-TOKEN=$GITHUB_TOKEN --env USERNAME=$USERNAME --env PASSWORD=$PASSWORD fedora_distro python3 dnf_collector.py -d Fedora -u $BACKEND_API -a https://kojipkgs.fedoraproject.org/packages -r https://src.fedoraproject.org/api/0/rpms

# CentOS:
docker build -t centos_distro -f centos.Dockerfile .
docker run --net host --shm-size=$SHM_SIZE --env GITHUB-TOKEN=$GITHUB_TOKEN --env USERNAME=$USERNAME --env PASSWORD=$PASSWORD centos_distro python3 dnf_collector.py -d CentOS -u $BACKEND_API -a https://vault.centos.org/8.4.2105 -r https://git.centos.org/api/0/rpms