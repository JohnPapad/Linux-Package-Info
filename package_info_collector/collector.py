import os
import ray
import sys
import json
import subprocess


info_to_parse = set(["Version", "Section", "Installed-Size", "Homepage", "Description", "Bugs"])


@ray.remote
class Packages:
    def __init__(self):
        self._packages = {}

    def add(self, name):
        if name in self._packages:
            return False
        else:
            self._packages[name] = {
                "Info": {},
                "Versions": {}
            }
            return True

    def exists(self, name):
        return name in self._packages

    def set_info(self, name, info):
        self._packages[name]["Info"] = info

    def set_version(self, name, version, arch):
        if version in self._packages[name]["Versions"]:
            self._packages[name]["Versions"][version]["arch"] = ["amd64", "i386"]
            return False # no need to re-calculate version's SWHID
        else:
            self._packages[name]["Versions"][version] = {
                "arch": [],
                "SWHID": None
            }
            if arch == "all":
                self._packages[name]["Versions"][version]["arch"] = ["amd64", "i386"]
            else:
                self._packages[name]["Versions"][version]["arch"] = [arch]
            return True # new version was added thus its corresponding SWHID needs to be calculated

    def set_version_SWHID(self, name, version, SWHID):
        self._packages[name]["Versions"][version]["SWHID"] = SWHID

    def get(self):
        return self._packages


def parse_packages_info():
    packages_output = (os.popen('apt list --all-versions')).readlines()
    print("Number of packages found:", len(packages_output))
    ids = []
    ray.init()
    packages = Packages.remote()
    for line in packages_output:
        line = line.rstrip("\n")
        if line == '' or line == "Listing...":
            continue
        id = parallel_processing.remote(line, packages)
        ids.append(id)

    ray.get(ids)
    packages = ray.get(packages.get.remote())
    print("Number of packages parsed: ", len(packages))
    # print(packages)
    with open('data_docker.json', 'w') as f:
        json.dump(packages, f)


def parse_package_version(package_name, string, packages):
    splitted_package_version = string.split(" ")
    package_version = splitted_package_version[1]
    package_arch = splitted_package_version[2]
    return packages.set_version.remote(package_name, package_version, package_arch), package_version
    

def parse_package_info(package_name, packages):
    info = {}
    info_output = (os.popen(f'apt show {package_name}')).readlines()
    for info_line in info_output:
        # print(info_line)
        splitted_info = info_line.rstrip('\n').split(": ")
        if len(splitted_info) == 1 and splitted_info != '':
            # description = splitted_info[0].lstrip(" ").rstrip("\n")
            # info["Description"] += description
            pass
        elif len(splitted_info) > 1:
            info_key = splitted_info[0]
            if info_key not in info_to_parse:
                continue
            info_value = splitted_info[1]
            info[info_key] = info_value

    packages.set_info.remote(package_name, info)


def calc_SWHID(package_name, package_version, packages):
    dir_name = package_name + '-' + package_version
    cmd = f'''
        mkdir output/{dir_name} && 
        cd output/{dir_name} &&
        apt-get source {package_name}={package_version} &&
        rm -rf *.dsc *.tar.* &&
        swh identify --no-filename $(ls -d */) &&
        cd ../../ &&
        rm -rf output/{dir_name}
    '''
    output = (os.popen(cmd)).readlines()
    SWHID = output[-1].rstrip("\n")
    packages.set_version_SWHID.remote(package_name, package_version, SWHID)


@ray.remote
def parallel_processing(line, packages):
    package_name, splitted_line = line.split("/")
    print(f"package: '{package_name}'")
    parse_info_flag = packages.add.remote(package_name)
    if parse_info_flag:
        parse_package_info(package_name, packages)

    calc_SWHID_flag, package_version = parse_package_version(package_name, splitted_line, packages)
    if calc_SWHID_flag:
        calc_SWHID(package_name, package_version, packages)


if __name__ == "__main__":
    print("started")
    parse_packages_info()
