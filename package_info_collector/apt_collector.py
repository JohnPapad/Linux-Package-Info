# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import ray
import json
import requests
import random
import time


info_to_parse = {
    "Section": "section", 
    "Installed-Size": "size", 
    "Homepage": "homepage", 
    "Description": "description", 
    "Original-Maintainer": "maintainer"
}


def get_pkg_version_hash_id(package_info, version):
    pkg_homepage = package_info.get("homepage", version)
    pkg_section = package_info.get("section", "")
    pkg_maintainer = package_info.get("maintainer", "")
    return version + pkg_homepage + pkg_maintainer + pkg_section


def parse_packages_info(distro, base_URL):
    packages_output = (os.popen('apt list --all-versions')).readlines()
    # random.shuffle(packages_output)
    print("Number of packages found:", (len(packages_output) // 2)-1)
    ray_ids = []
    ray.init()
    pkg_counter = 0
    start_time = time.time()
    for line in packages_output:
        line = line.rstrip("\n")
        if line == '' or line == "Listing...":
            continue

        if len(ray_ids) > 50:
            num_ready = pkg_counter-50
            ray.wait(ray_ids, num_returns=num_ready)

        ray_id = parallel_processing.remote(distro, base_URL, line, pkg_counter)
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
    

def get_package_versions(string):
    splitted_package_version = string.split(" ")
    package_version = splitted_package_version[1]
    package_arch = splitted_package_version[2]
    return {
        package_version: package_arch
    }


def convert_size_to_MBs(size):
    size = size.replace(",", ".")
    number, unit = size.split(" ")
    number = float(number)

    if unit == "B":
        number /= 1024 * 1024
    elif unit == "kB":
        number /= 1024
    elif unit == "MB":
        pass
    else: # GB
        number *= 1024

    return number


def extract_package_info(package_name):
    info = {}
    info_output = (os.popen(f'apt show {package_name}')).readlines()
    for info_line in info_output:
        # print(info_line)
        splitted_info = info_line.rstrip('\n').split(": ")
        if len(splitted_info) == 1 and splitted_info != '':
            # description = splitted_info[0].lstrip(" ").rstrip("\n")
            # info["description"] += " " + description
            pass
        elif len(splitted_info) > 1:
            info_key = splitted_info[0]
            if info_key not in info_to_parse:
                continue

            info_key = info_to_parse[info_key]
            info_value = splitted_info[1]
            if info_key == "size":
                info_value = convert_size_to_MBs(info_value)

            info[info_key] = info_value

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


def get_package_existing_versions(package_versions_list):
    versions = {}
    for version_info in package_versions_list:
        versions[version_info["version"]] = version_info

    return versions


def fetch_package_info(distro, base_URL, package_name):
    '''
    HTTP call to backend to fetch package info (if it already exists in DB)
    '''
    URL_params = {
        "distro": distro,
        "name": package_name
    }

    try:
        response = requests.get(f'{base_URL}/packages/', params=URL_params)
        if response.status_code != 200:
            return None

        # successfully retrieved package info
        res_data = response.json() # expecting a list with 1 item max
        assert len(res_data) < 2, f'duplicate packages "{package_name}" were found'
        if len(res_data) == 1:
            return res_data[0]
    except:
        pass

    return None


def add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, package_id):
    if len(pkg_versions_to_add) == 0:
        return
    try:
        requests.post(f'{base_URL}/packages/{package_id}/versions/', json=pkg_versions_to_add)
    except:
        pass


def update_existing_package_versions(base_URL, pkg_versions_to_update):
    '''
    update versions' info of a existing package in the db
    '''
    for version_id, updated_version_archs in pkg_versions_to_update.items():
        payload = {
            "architecture": updated_version_archs
        }
        try:
            requests.patch(f'{base_URL}/packages/versions/{version_id}/', json=payload)
        except:
            pass


def add_new_package(distro, base_URL, package_name, package_info, pkg_versions_to_add):
    '''
    save info about a new package in the db
    '''
    package_info["versions"] = pkg_versions_to_add
    package_info["distro"] = distro
    package_info["name"] = package_name

    print("package_info: ", package_info)

    try:
        res = requests.post(f'{base_URL}/packages/', json=package_info)
        print("status: ", res.status_code, res.json())
    except:
        pass
    

@ray.remote
def parallel_processing(distro, base_URL, line, i):
    package_name, splitted_line = line.split("/")
    print(f"package: '{package_name}' - #{i}")
    package_versions = get_package_versions(splitted_line)

    pkg_existing_info = fetch_package_info(distro, base_URL, package_name)

    if pkg_existing_info == None: # package not included
        package_info = extract_package_info(package_name)
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
            # if the particular version supports both architectures no need to update (already supports one of the 2 archs)
                existing_version_id = pkg_existing_versions[package_version]["id"]
                pkg_versions_to_update[existing_version_id] = "amd64 i386"
        else: # new version
            if package_arch == "all":
                package_arch = "amd64 i386"

            pkg_versions_to_add.append({
                "version": package_version,
                "architecture": package_arch
            })
 
    if pkg_existing_info != None: # package is already included no need to re-entry its info to the db
        package_id = pkg_existing_info["id"]
        add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, package_id) # add only the possible new versions
        update_existing_package_versions(base_URL, pkg_versions_to_update) # update versions' info of existing packages
    else: # package not included
        add_new_package(distro, base_URL, package_name, package_info, pkg_versions_to_add)

    return f"-> Package #{i} - {package_name} collected"


if __name__ == "__main__":
    print("-> Package collector started..")
    distro="Ubuntu"
    base_URL="http://localhost:8000/api/v1"
    parse_packages_info(distro, base_URL)