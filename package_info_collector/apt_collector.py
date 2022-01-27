# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import ray
import json
import requests
import random
import time
import argparse
from os import getenv


github_API_headers = {
    'Authorization': f"token {getenv('GITHUB-TOKEN')}"
}


info_to_parse = {
    "Section": "section",
    "Homepage": "homepage",
    "Description": "description",
    "Description-en": "description",
    "Maintainer": "maintainer",
    "Original-Maintainer": "orig_maintainer",
    # "Installed-Size": "size",
    # "Filename": "binary_URL"
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
                packages_versions[pkg_name][pkg_version]["architecture"] += " " + pkg_arch

        # print("-"*35)

    # print(packages_versions)
    print("-> Number of packages found:", len(packages_versions))
    return packages_versions


def parse_packages_info(distro, base_URL, max_concurrency, distro_archives_URL):
    packages_versions = group_package_versions()
    ray_ids = []
    ray.init()
    pkg_counter = 0
    start_time = time.time()
    for pkg_name, pkg_versions in packages_versions.items():
        if len(ray_ids) > max_concurrency:
            num_ready = pkg_counter-max_concurrency
            ray.wait(ray_ids, num_returns=num_ready)

        ray_id = parallel_processing.remote(distro, base_URL, pkg_name, pkg_versions, distro_archives_URL, pkg_counter)
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

    return package_version, package_arch


def extract_package_license_from_github_repo(pkg_repo_id):
    '''
    attempting to extract license from the package's github repo through its API
    '''    
    try:
        response = requests.get(f'https://api.github.com/repos/{pkg_repo_id}', headers=github_API_headers)
        if response.status_code != 200:
            return None

        license_info = response.json().get("license")
        if not license_info:
            pkg_license = "No license"
        else:
            pkg_license = license_info.get("name")

        return pkg_license
    except:
        return None


def remove_substrings(string, substrings_to_remove):
    for sub_str in substrings_to_remove:
        string = string.replace(sub_str, "")
    return string


def extract_package_license_from_salsa_repo(pkg_repo_id):
    '''
    attempting to extract license from Debian's salsa repo through its API (follows GitLab's API format)
    '''
    pkg_repo_id = pkg_repo_id.replace("/", "%2F")
    try:
        response = requests.get(f"https://salsa.debian.org/api/v4/projects/{pkg_repo_id}?license=true")
        if response.status_code != 200:
            return None

        license_info = response.json().get("license")
        if not license_info:
            pkg_license = "No license"
        else:
            pkg_license = license_info.get("name")

        return pkg_license
    except:
        return None


def extract_package_repo_URL_from_dsc_file(pkg_dsc_file_URL):
    try:
        response = requests.get(pkg_dsc_file_URL)
        if response.status_code != 200:
            return None

        repo_URL = None
        for line in response.text.split('\n'):
            if line.startswith('Vcs-Browser: '):
                repo_URL = line.split(": ")[1]
                break

        return repo_URL
    except:
        return None


def extract_package_repo_id(pkg_repo_URL, base_URL):
    pkg_repo_id = remove_substrings(pkg_repo_URL, [base_URL, ".git"])
    pkg_repo_id = pkg_repo_id.split("/tree/")[0]
    return pkg_repo_id


def extract_package_version_info(package_name, package_version, distro_archives_URL):
    info_output = (os.popen(f'apt-cache show {package_name}={package_version} | grep -wE "^Installed-Size|^Filename"')).readlines()
    try:
        size = info_output[0].rstrip('\n').split("Installed-Size: ")[1] # Installed-Size: <Kbs>
        size = float(size.replace(",", "."))
    except:
        size = None

    try:
        binary_URL = info_output[1].rstrip('\n').split("Filename: ")[1] # Filename: <archive_path>
        binary_URL = f'{distro_archives_URL}/{binary_URL}'
    except:
        binary_URL= None

    return size, binary_URL


def extract_package_info(package_name, package_versions, distro_archives_URL):
    info = {}
    info_output = (os.popen(f'apt-cache show {package_name} | grep -wE "^Installed-Size|^Filename|^Description|^Version|^Maintainer|^Original-Maintainer|^Section|^Homepage"')).readlines()
    cur_version = None
    for info_line in info_output:
        # print(info_line)
        splitted_info = info_line.rstrip('\n').split(": ")
        if len(splitted_info) != 2:
            continue

        info_key, info_value = splitted_info
        if info_key == "Version":
            cur_version = info_value
        elif info_key == "Installed-Size":
            assert cur_version in package_versions, f"ERROR in package ({package_name}), version ({cur_version}) size extraction: unknown version (should have been previously found)"
            package_versions[cur_version]["size"] = float(info_value.replace(",", "."))
        elif info_key == "Filename":
            assert cur_version in package_versions, f"ERROR in package ({package_name}), version ({cur_version}) binary URL extraction: unknown version (should have been previously found)"
            binary_URL = f'{distro_archives_URL}/{info_value}'
            package_versions[cur_version]["binary_URL"] = binary_URL
        elif info_key not in info_to_parse or info_to_parse[info_key] in info:
            continue
        else:
            info[info_to_parse[info_key]] = info_value

    # print("/" * 35)
    try:
        info_output = (os.popen(f'apt-cache showsrc {package_name} | grep -wE "^Vcs-Browser"')).readline()
        pkg_repo_URL = info_output.split("Vcs-Browser: ")[1].rstrip("\n")
    except:
        pkg_repo_URL = None

    if pkg_repo_URL is not None:
        info["repo_URL"] = pkg_repo_URL
    # print(pkg_repo_URL)
    # print("/" * 35)

    if "maintainer" in info and "orig_maintainer" in info:
        # keep only the original maintainer field
        info["maintainer"] = info.pop("orig_maintainer")
    elif "orig_maintainer" in info:
        info["maintainer"] = info.pop("orig_maintainer")

    pkg_homepage = info.get("homepage")
    # pkg_binary_URL = info.get("binary_URL")

    pkg_license = None
    if pkg_repo_URL and pkg_repo_URL.startswith("https://salsa.debian.org/"):
        pkg_repo_id = extract_package_repo_id(pkg_repo_URL, "https://salsa.debian.org/")
        pkg_license = extract_package_license_from_salsa_repo(pkg_repo_id)
    elif pkg_repo_URL and pkg_repo_URL.startswith("https://github.com/"):
        pkg_repo_id = extract_package_repo_id(pkg_repo_URL, "https://github.com/")
        pkg_license = extract_package_license_from_github_repo(pkg_repo_id)
    elif pkg_homepage and pkg_homepage.startswith("https://salsa.debian.org/"):
        if pkg_repo_URL is None:
            info["repo_URL"] = pkg_homepage

        pkg_repo_id = extract_package_repo_id(pkg_homepage, "https://salsa.debian.org/")
        pkg_license = extract_package_license_from_salsa_repo(pkg_repo_id)
    elif pkg_homepage and pkg_homepage.startswith("https://github.com/"):
        if pkg_repo_URL is None:
            info["repo_URL"] = pkg_homepage

        pkg_repo_id = extract_package_repo_id(pkg_homepage, "https://github.com/")
        pkg_license = extract_package_license_from_github_repo(pkg_repo_id)

    # elif pkg_binary_URL:
    #     pkg_dsc_file_URL = remove_substrings(pkg_binary_URL, ["_amd64", "_i386", "_all"])
    #     pkg_dsc_file_URL = pkg_dsc_file_URL[:-3] + "dsc"
    #     pkg_repo_URL = extract_package_repo_URL_from_dsc_file(pkg_dsc_file_URL)

    #     if pkg_repo_URL:
    #         info["repo_URL"] = pkg_repo_URL

    #         if pkg_repo_URL.startswith("https://github.com/"):
    #             pkg_repo_id = extract_package_repo_id(pkg_repo_URL, "https://github.com/")
    #             pkg_license = extract_package_license_from_github_repo(pkg_repo_id)
    #         elif pkg_repo_URL.startswith("https://salsa.debian.org/"):
    #             pkg_repo_id = extract_package_repo_id(pkg_repo_URL, "https://salsa.debian.org/")
    #             pkg_license = extract_package_license_from_salsa_repo(pkg_repo_id)

    # print(pkg_license)
    if pkg_license is not None:
        info["license"] = pkg_license

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
def parallel_processing(distro, base_URL, package_name, package_versions, distro_archives_URL, i):
    # print(f"-> Now processing package: '{package_name}' - #{i}")
    report_msg = f"-> Package #{i} - {package_name}: "
    pkg_existing_info = fetch_package_info(distro, base_URL, package_name)

    if pkg_existing_info is None: # package not included
        package_info = extract_package_info(package_name, package_versions, distro_archives_URL)
        pkg_versions_to_add = []
        for pkg_version, pkg_version_info in package_versions.items():
            pkg_versions_to_add.append({
                "version": pkg_version,
                **pkg_version_info
            })

        package_saved_flag = add_new_package(distro, base_URL, package_name, package_info, pkg_versions_to_add)
        if package_saved_flag:
            report_msg += "successfully added"
        else:
            report_msg += "failed to be added"
    else: # package is included not need to re-parse its core info
        pkg_existing_versions = get_package_existing_versions(pkg_existing_info['versions'])
        pkg_versions_to_add = []
        for pkg_version, pkg_version_info in package_versions.items():
            if pkg_version in pkg_existing_versions:
                continue

            # new version
            pkg_version_size, pkg_version_binary_URL = extract_package_version_info(package_name, pkg_version, distro_archives_URL)
            pkg_versions_to_add.append({
                "version": pkg_version,
                "architecture": pkg_version_info["architecture"],
                "size": pkg_version_size,
                "binary_URL": pkg_version_binary_URL
            })

        new_versions_flag = add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, pkg_existing_info["id"]) # add only the possible new versions
        if new_versions_flag:
            report_msg += "successfully added new versions "
        else:
            report_msg += "no new version was added "

    return report_msg
    

if __name__ == "__main__":
    cmdParser = argparse.ArgumentParser(
        allow_abbrev=False, 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A script that parses useful info about all software packages (along with all their corresponding available versions) of a Linux distribution, that uses the 'apt' package manager, and sends them to a backend through an API in order to be saved in a database",
        epilog='''for example in order to parse info about the Ubuntu:20.04 packages (given the fact that the backend runs on the same machine):
$ python3 apt_collector.py -d Ubuntu:20.04 -u http://localhost:8000/api/v1 -a http://archive.ubuntu.com/ubuntu/'''
    )
    cmdParser.add_argument('--max-concurrency', '-c', type=int, dest='max_concurrency', metavar='<int>', help='[default: 50] Number of maximum packages that will be processed concurrently', default=50)
    cmdParser.add_argument('--distro', '-d', type=str, dest='distro', metavar='<str>', help='The linux distribution name', required=True)
    cmdParser.add_argument('--API-URL', '-u', type=str, dest='base_URL', metavar='<url>', help="Backend's API base URL", required=True)
    cmdParser.add_argument('--archives-url', '-a', type=str, dest='distro_archives_URL', metavar='<url>', help="Linux distribution's archives base URL", required=True)

    cmdArgs = vars(cmdParser.parse_args())

    info_output = (os.popen(f'lsb_release -r')).readline()
    distro_release = info_output.rstrip("\n").split("Release:")[1].lstrip("\t")
    distro = f"{cmdArgs['distro']}:{distro_release}"

    print("--> Linux Package Collector started..")
    print('-> Command line arguments:')
    print('- Linux Distribution:', distro)
    print("- Backend's API base URL:", cmdArgs['base_URL'])
    print("- Linux distribution's archives base URL:", cmdArgs['distro_archives_URL'])
    print('- Number of maximum packages to be processed concurrently:', cmdArgs['max_concurrency'])
    print("-" * 35)

    parse_packages_info(distro, cmdArgs['base_URL'], cmdArgs['max_concurrency'], cmdArgs['distro_archives_URL'])
    print("--> Linux Package Collector finished..")
