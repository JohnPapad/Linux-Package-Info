# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import ray
import json
import requests
import random
import time


# info_to_parse = set(["Section", "Installed-Size", "Homepage", "Description", "Original-Maintainer"])
info_to_parse = {
    "Section": "section", 
    "Installed-Size": "size", 
    "Homepage": "homepage", 
    "Description": "description", 
    "Original-Maintainer": "maintainer"
}


@ray.remote
class Packages:
    def __init__(self):
        self._packages = {}
        self._versions_SWHID_cache = {}

    def exists(self, name):
        return name in self._packages

    def get_info(self, name):
        return self._packages.get(name, None)

    def add(self, name, info):
        self._packages[name] = info

    def add_versions(self, name, versions_to_add):
        self._packages[name]["versions"].extend(versions_to_add)

    def update_versions(self, name, versions_to_update):
        pass

    def set_version_SWHID_cache(self, version_hash_id, SWHID, SWHID_exists):
        if SWHID == None:
            return

        self._versions_SWHID_cache[version_hash_id] = {
            "swhid": SWHID,
            "swhid_exists": SWHID_exists
        }

    def check_version_SWHID_cache(self, version_hash_id):
        if version_hash_id not in self._versions_SWHID_cache:
            return None, None

        SWHID = self._versions_SWHID_cache[version_hash_id]["swhid"]
        SWHID_exists = self._versions_SWHID_cache[version_hash_id]["swhid_exists"]
        return SWHID, SWHID_exists

    def get(self):
        return self._packages


def get_pkg_version_hash_id(package_info, version):
    pkg_homepage = package_info.get("homepage", version)
    pkg_section = package_info.get("section", "")
    pkg_maintainer = package_info.get("maintainer", "")
    return version + pkg_homepage + pkg_maintainer + pkg_section


def parse_packages_info():
    
    packages_output = (os.popen('apt list --all-versions')).readlines()
    random.shuffle(packages_output)
    print("Number of packages found:", (len(packages_output) // 2)-1)
    ray_ids = []
    ray.init()
    packages_obj = Packages.remote()
    pkg_counter = 0
    start_time = time.time()
    for line in packages_output:
        line = line.rstrip("\n")
        if line == '' or line == "Listing...":
            continue
        
        if len(ray_ids) > 50:
            num_ready = pkg_counter-50
            ray.wait(ray_ids, num_returns=num_ready)

        ray_id = parallel_processing.remote(line, packages_obj, pkg_counter)
        ray_ids.append(ray_id)
        pkg_counter += 1

    unfinished = ray_ids
    while unfinished:
        # Returns the first ObjectRef that is ready.
        finished, unfinished = ray.wait(unfinished, num_returns=1)
        msg = ray.get(finished)
        print(msg)

    end_time = time.time() 
    print('-> Elapsed time: ', end_time - start_time)

    packages = ray.get(packages_obj.get.remote())
    print("Number of packages parsed: ", len(packages))
    

def get_package_versions(string):
    splitted_package_version = string.split(" ")
    package_version = splitted_package_version[1]
    package_arch = splitted_package_version[2]
    return {
        package_version: package_arch
    }


def get_package_info(package_name):
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
            
            info_key = info_to_parse[info_key]
            info[info_key] = splitted_info[1] # info value

    return info  


def SWHID_resolve(SWHID):
    if SWHID == None:
        return None
        
    exists = None
    try:
        response = requests.get('https://archive.softwareheritage.org/api/1/resolve/' + SWHID)
        if response.status_code == 200:
            exists = True
        elif response.status_code == 404:
            exists = False
    except:
        pass
        
    return exists
    

def calc_SWHID(package_name, package_version):
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
    if not SWHID.startswith("swh"):
        SWHID = None

    # print("SWHID", SWHID, " package", package_name, " version", package_version)
    return SWHID


def save_package(packages, package_name, pkg_existing_info, package_info, pkg_versions_to_add, pkg_versions_to_update):
    if package_info == None: # package is already included no need to re-entry its info to the db
        # add only the possible new versions
        if len(pkg_versions_to_add) != 0:
            package_id = pkg_existing_info["id"]
            try:
                response = requests.post(f'http://localhost:8000/api/v1/packages/{package_id}/versions', data=pkg_versions_to_add)
                if response.status_code == 201: # created
                    ray.get([packages.add_versions.remote(package_name, pkg_versions_to_add)])[0]
            except:
                pass
    else: # package not included
        package_info["versions"] = pkg_versions_to_add
        package_info["distro"] = "Ubuntu"
        try:
            response = requests.post('http://localhost:8000/api/v1/packages/', data=package_info)
            if response.status_code == 201: # created
                data = response.json()
                print("response data: ", data)
                ray.get([packages.add.remote(package_name)])[0]
        except:
            pass


def get_package_existing_versions(package_versions):
    versions = {}
    for version_info in package_versions:
        versions[version_info["version"]] = version_info

    return versions


@ray.remote
def parallel_processing(line, packages, i):
    package_name, splitted_line = line.split("/")
    print(f"package: '{package_name}' - #{i}")
    package_versions = get_package_versions(splitted_line)

    pkg_existing_info = ray.get([packages.get_info.remote(package_name)])[0]
    if pkg_existing_info == None: # package not included
        package_info = get_package_info(package_name)
        pkg_existing_versions = None
    else: # package is included not need to re-parse its info
        package_info = None
        pkg_existing_versions = get_package_existing_versions(pkg_existing_info['versions'])

    pkg_versions_to_add = []
    pkg_versions_to_update = {}
    for package_version, package_arch in package_versions.items():
        if pkg_existing_versions and package_version in pkg_existing_versions: # version exists
            existing_version_arch = pkg_existing_versions[package_version]["architecture"]
            if package_arch != existing_version_arch and existing_version_arch != "amd64 i386":
            # if the particular version supports both architectures no need to update
                pkg_versions_to_update[package_version] = "amd64 i386" 
        else: # new version
            if pkg_existing_info:
                pkg_version_hash_id = get_pkg_version_hash_id(pkg_existing_info, package_version)
            else:
                pkg_version_hash_id = get_pkg_version_hash_id(package_info, package_version)

            SWHID, SWHID_exists = ray.get([packages.check_version_SWHID_cache.remote(pkg_version_hash_id)])[0]
            if SWHID == None:
                SWHID = calc_SWHID(package_name, package_version)
                SWHID_exists = SWHID_resolve(SWHID) 
                packages.set_version_SWHID_cache.remote(pkg_version_hash_id, SWHID, SWHID_exists)
    
            pkg_versions_to_add.append({
                "version": package_version,
                "swhid": SWHID,
                "swhid_exists": SWHID_exists,
                "architecture": package_arch
            })
 
    save_package(packages, package_name, pkg_existing_info, package_info, pkg_versions_to_add, pkg_versions_to_update)
    return f"-> Package #{i} - {package_name} collected"


if __name__ == "__main__":
    print("-> Package collector started..")
    parse_packages_info()
