# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import ray
import json
import requests
import random
import time
import argparse


info_to_parse = {
    "Section": "section",
    # "Installed-Size": "size",
    "Homepage": "homepage",
    "Description": "description",
    "Original-Maintainer": "maintainer"
}


def group_package_versions():
    packages_output = (os.popen('apt list --all-versions')).readlines()
    packages_versions = {}
    for line in packages_output:
        line = line.rstrip("\n")
        # print(line)
        if line == '' or line == "Listing...":
            continue

        pkg_name, splitted_line = line.split("/")
        pkg_version, pkg_arch = extract_package_version(splitted_line)

        # print(pkg_name, pkg_version, pkg_arch)

        if pkg_name not in packages_versions:
            packages_versions[pkg_name] = {
                pkg_version: {
                    "architecture": pkg_arch
                }
            }
        else:
            if pkg_version not in packages_versions[pkg_name]: # package version not in existing versions
                packages_versions[pkg_name][pkg_version] = {
                    "architecture": pkg_arch
                }
            else: # one of the two archs already exists
                packages_versions[pkg_name][pkg_version]["architecture"] = "amd64 i386"

        # print("-"*35)

    # print(packages_versions)
    print("-> Number of packages found:", len(packages_versions))
    return packages_versions


def parse_packages_info(distro, base_URL, max_concurrency):
    packages_versions = group_package_versions()
    ray_ids = []
    ray.init()
    pkg_counter = 0
    start_time = time.time()
    for pkg_name, pkg_versions in packages_versions.items():
        if len(ray_ids) > max_concurrency:
            num_ready = pkg_counter-max_concurrency
            ray.wait(ray_ids, num_returns=num_ready)

        ray_id = parallel_processing.remote(distro, base_URL, pkg_name, pkg_versions, pkg_counter)
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
    

def extract_package_version(string):
    splitted_package_version = string.split(" ")
    package_version = splitted_package_version[1]
    package_arch = splitted_package_version[2]
    if package_arch == "all":
        package_arch = "amd64 i386"

    return package_version, package_arch


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


def extract_package_versions_size(package_name, package_versions):
    info_output = (os.popen(f"apt show {package_name} -a | grep -w 'Version\|Installed-Size'")).readlines()
    cur_version = None
    for info_line in info_output:
        info_key, info_value = info_line.rstrip('\n').split(": ")
        if info_key == "Version":
            cur_version = info_value
        elif info_key == "Installed-Size":
            assert cur_version in package_versions, f"ERROR in package ({package_name}), version ({cur_version}) size extraction: unknown version (should have been previously found)"
            package_versions[cur_version]["size"] = convert_size_to_MBs(info_value)
        else:
            assert True, f"ERROR in package ({package_name}), version ({cur_version}) size extraction: unknown info key word ({info_key})"


def extract_package_info(package_name):
    info = {}
    info_output = (os.popen(f'apt show {package_name}')).readlines()
    for info_line in info_output:
        # print(info_line)
        splitted_info = info_line.rstrip('\n').split(": ")
        if len(splitted_info) > 1:
            info_key = splitted_info[0]
            if info_key not in info_to_parse:
                continue

            info_key = info_to_parse[info_key]
            info[info_key] = splitted_info[1]

    return info


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
        assert len(res_data) < 2, f'ERROR in fetching package info: duplicate packages "{package_name}" were found'
        if len(res_data) == 1:
            return res_data[0]
    except:
        pass

    return None


def add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, package_id):
    if len(pkg_versions_to_add) == 0:
        return False

    try:
        res = requests.post(f'{base_URL}/packages/{package_id}/versions/', json=pkg_versions_to_add)
        if res.status_code == 201:
            return True
    except:
        pass

    return False


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

    # print("package_info: ", package_info)

    try:
        res = requests.post(f'{base_URL}/packages/', json=package_info)
        if res.status_code == 201:
            return True
        # print("status: ", res.status_code, res.json())
    except:
        pass

    return False
    

@ray.remote
def parallel_processing(distro, base_URL, package_name, package_versions, i):
    # print(f"-> Now processing package: '{package_name}' - #{i}")

    pkg_existing_info = fetch_package_info(distro, base_URL, package_name)

    if pkg_existing_info == None: # package not included
        package_info = extract_package_info(package_name)
        extract_package_versions_size(package_name, package_versions)
        pkg_existing_versions = None
    else: # package is included not need to re-parse its info
        package_info = None
        pkg_existing_versions = get_package_existing_versions(pkg_existing_info['versions'])

    # print("package_versions", package_versions)
    pkg_versions_to_add = []
    pkg_versions_to_update = {}
    for pkg_version, pkg_version_info in package_versions.items():
        pkg_version_arch = pkg_version_info["architecture"]
        if pkg_existing_versions and pkg_version in pkg_existing_versions: # version exists
            existing_version_arch = pkg_existing_versions[pkg_version]["architecture"]
            if pkg_version_arch != existing_version_arch and existing_version_arch != "amd64 i386":
            # if the particular version supports both architectures no need to update (already supports one of the 2 archs)
                existing_version_id = pkg_existing_versions[pkg_version]["id"]
                pkg_versions_to_update[existing_version_id] = "amd64 i386"
        else: # new version
            pkg_versions_to_add.append({
                "version": pkg_version,
                "architecture": pkg_version_arch,
                "size": pkg_version_info["size"]
            })

    report_msg = f"-> Package #{i} - {package_name}: "
    if pkg_existing_info != None: # package is already included no need to re-entry its info to the db
        package_id = pkg_existing_info["id"]
        new_versions_flag = add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, package_id) # add only the possible new versions
        update_versions_flag = update_existing_package_versions(base_URL, pkg_versions_to_update) # update versions' info of existing packages
        
        if new_versions_flag:
            report_msg += "successfully added new versions "
        else:
            report_msg += "no new version was added "

        # if update_versions_flag:
        #     report_msg += "- successfully updated existing versions"
        # else:
        #     report_msg += "- failed to update existing versions"

    else: # package not included
        package_saved_flag = add_new_package(distro, base_URL, package_name, package_info, pkg_versions_to_add)
        if package_saved_flag:
            report_msg += "successfully added"
        else:
            report_msg += "failed to be added"

    return report_msg
    

if __name__ == "__main__":
    cmdParser = argparse.ArgumentParser(
        allow_abbrev=False, 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A script that parses useful info about all software packages (along with all their corresponding available versions) of a Linux distribution, that uses the 'apt' package manager, and sends them to a backend through an API in order to be saved in a database",
        epilog='''for example in order to parse info about the Ubuntu:20.04 packages (given the fact that the backend runs on the same machine):
$ python3 apt_collector.py -d Ubuntu:20.04 -u http://localhost:8000/api/v1'''
    )
    cmdParser.add_argument('--max-concurrency', '-c', type=int, dest='max_concurrency', metavar='<int>', help='[default: 50] Number of maximum packages that will be processed concurrently', default=50)
    cmdParser.add_argument('--distro', '-d', type=str, dest='distro', metavar='<str>', help='The linux distribution name', required=True)
    cmdParser.add_argument('--url', '-u', type=str, dest='base_URL', metavar='<url>', help="API's base URL", required=True)

    cmdArgs = vars(cmdParser.parse_args())

    print("--> Linux Package Collector started..")
    print('-> Command line arguments:')
    print('- Linux Distribution: ', cmdArgs['distro'])
    print("- API's base URL: ", cmdArgs['base_URL'])
    print('- Number of maximum packages to be processed concurrently: ', cmdArgs['max_concurrency'])
    print("-" * 35)

    parse_packages_info(cmdArgs['distro'], cmdArgs['base_URL'], cmdArgs['max_concurrency'])
    print("--> Linux Package Collector finished..")
