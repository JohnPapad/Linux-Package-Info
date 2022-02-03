# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from rest_framework.renderers import BaseRenderer
from django.utils.encoding import smart_text
from .serializers import CreateDockerfileSerializer
from datetime import datetime
import json


distros_docker_repos = {
    "Ubuntu": "ubuntu",
    "Debian": "debian",
    "Kali": "kalilinux/kali-last-release",
    "Fedora": 'fedora',
    "centos": "centos"
}


class DockerfileRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'
    serializer_class = CreateDockerfileSerializer

    def render(self, data, media_type=None, renderer_context=None):
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return json.dumps(serializer.errors)

        timestamp = datetime.now().replace(second=0, microsecond=0)
        dockerfile = f'# Generated by PKGman at {timestamp}\n'
        if data['distro_name'] == 'Ubuntu':
            dockerfile += f"FROM ubuntu:{data['distro_version']}"
        elif data['distro_name'] == 'Debian':
            dockerfile += f"FROM debian:{data['distro_version']}"
        elif data['distro_name'] == 'Kali':
            dockerfile += "FROM kalilinux/kali-last-release:latest"
        elif data['distro_name'] == 'Fedora':
            dockerfile += f"FROM fedora:34"
        elif data['distro_name'] == 'CentOS':
            dockerfile += "FROM centos:centos8.4.2105"
            dockerfile += '''
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-* && \\
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*

RUN dnf install -y yum-utils && \\
    yum-config-manager --enable powertools && \\
    yum-config-manager --enable ha && \\
    yum-config-manager --enable plus'''

        install_pkg_cmd = ''
        if data['distro_type'] == "deb":
            dockerfile += "\n\nRUN apt-get update"
            install_pkg_cmd = "apt-get install"
        elif data['distro_type'] == "rpm":
            install_pkg_cmd = "dnf install"

        dockerfile += '\n\nRUN '
        for i, pkg in enumerate(data['packages']):
            dockerfile += f'{install_pkg_cmd} {pkg} -y'
            if i == len(data['packages'])-1:
                break
            dockerfile += " && \\ \n    "

        return smart_text(dockerfile, encoding=self.charset)
