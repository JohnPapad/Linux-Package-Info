# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import ray
import requests
import time
import argparse
from os import getenv


github_API_headers = {
    'Authorization': f"token {getenv('GITHUB-TOKEN')}"
}


info_to_parse = {
    "License": "license",
    "URL": "homepage",
    "Summary": "description"
    # "Size": "size",
    # "Source": "binary_URL",
}

centOS_repos = {
    "appstream": "AppStream",
    "baseos": "BaseOS",
    "ha": "HighAvailability",
    "powertools": "PowerTools",
    "plus": "centosplus",
    "extras": "extras"
}


def group_packages():
    packages_output = (os.popen('dnf list all')).readlines()
    packages = {}
    for line in packages_output:
        try:
            pkg_name, _ = line.split(" ")[0].split(".")
        except:
            continue

        if pkg_name not in packages:
            packages[pkg_name] = None

    print("-> Number of packages found:", len(packages))
    return packages


def parse_packages_info(distro, base_URL, max_concurrency, distro_archives_URL, distro_repos_URL):
    packages = group_packages()

    ray_ids = []
    ray.init()
    pkg_counter = 0
    start_time = time.time()
    for pkg_name in packages:
        if len(ray_ids) > max_concurrency:
            num_ready = pkg_counter-max_concurrency
            ray.wait(ray_ids, num_returns=num_ready)

        ray_id = parallel_processing.remote(distro, base_URL, pkg_name, distro_archives_URL, distro_repos_URL, pkg_counter)
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


def extract_package_info_from_github_repo(pkg_repo_id):
    '''
    attempting to extract maintainer from the package's github repo through its API
    '''    
    try:
        response = requests.get(f'https://api.github.com/repos/{pkg_repo_id}', headers=github_API_headers)
        if response.status_code != 200:
            return None

        return response.json()['owner'].get("html_url")
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
            pkg_license = "No license. All rights reserved"
        else:
            pkg_license = license_info.get("name")

        return pkg_license
    except:
        return None


def extract_package_repo_id(pkg_repo_URL, base_URL):
    pkg_repo_id = remove_substrings(pkg_repo_URL, [base_URL, ".git"])
    pkg_repo_id = pkg_repo_id.split("/tree/")[0]
    return pkg_repo_id


def extract_package_version_info(pkg_name_version_release):
    info_output = (os.popen(f'dnf info {pkg_name_version_release} | grep -wE "^Size|^Architecture|^Repository|^From repo"')).readlines()
    version_arch = None
    version_size = None
    version_repo = None
    cur_version_arch = None
    for info_line in info_output:
        try:
            info_key, info_value = info_line.rstrip('\n').split(": ")
            info_key = info_key.rstrip(" ")
        except:
            continue

        if info_key == "Architecture":
            cur_version_arch = info_value
            if version_arch is None:
                version_arch = info_value
            else:
                version_arch += " " + info_value
        elif info_key == "Size":
            if version_size is None or cur_version_arch == "x86_64":
                version_size = convert_size_to_kBs(info_value)
        elif info_key == "Repository" or info_key == "From repo":
            if info_value in centOS_repos:
                version_repo = info_value

    return version_arch, version_size, version_repo


def extract_package_version_names(package_name):
    package_versions = {}
    info_output = (os.popen(f'dnf info {package_name} | grep -wE "^Source"')).readlines()
    for info_line in info_output:
        try:
            _, info_value = info_line.rstrip('\n').split(": ")
            version_full_name = info_value[:-8]
            _, version_name, version_release = version_full_name.split("-")
            version_key = f'{version_name}-{version_release}'
            package_versions[version_key] = {
                "full_name": version_full_name,
                "name": version_name,
                "release": version_release
            }
        except:
            continue

    return package_versions


def convert_size_to_kBs(size):
    try:
        size = size.replace(",", ".")
        number, unit = size.split(" ")
        number = float(number)
    except:
        return None

    if unit == "B":
        number /= 1024
    elif unit == "k":
        pass
    elif unit == "M":
        number *= 1024
    else: # GB
        number *= 1024 * 1024

    return number


def extract_package_info_from_distro_repo(distro_repos_URL, package_name):
    if package_name is None:
        return None, None

    try:
        response = requests.get(f'{distro_repos_URL}/{package_name}')
        if response.status_code != 200:
            # print("-> distro repo failure response: ", response.json())
            return None, None

        repo_URL = response.json().get("full_url")
        maintainer = response.json()['user'].get("full_url")
        return repo_URL, maintainer
    except:
        return None, None


def extract_package_info_from_distro_repo2(distro_repos_URL, package_name):
    if package_name is None:
        return None

    try:
        response = requests.get(f'{distro_repos_URL}/{package_name}')
        if response.status_code != 200:
            # print("-> distro repo failure response: ", response.json())
            return None

        maintainer = response.json()['user'].get("fullname")
        return maintainer
    except:
        return None


def extract_base_package_name(package_name):
    base_pkg_name = package_name.split("-")
    if len(base_pkg_name) == 1:
        return None

    if len(base_pkg_name) == 2:
        return base_pkg_name[0]

    return "-".join(base_pkg_name[:-1]) # wipe out the last token


def fix_package_versions_binary_URLs(package_base_name, package_name, versions_info):
    if package_base_name is None:
        return

    for key, info in versions_info.items():
        versions_info[key]["binary_URL"] = info["binary_URL"].replace(package_name, package_base_name)


def extract_package_info(package_name, distro, distro_archives_URL, distro_repos_URL):
    info = {}
    versions_info = {}
    info_output = (os.popen(f'dnf info {package_name} | grep -wE "^Size|^Summary|^License|^Version|^Release|^Source|^URL|^Architecture|^Repository|^From repo"')).readlines() #--showduplicates
    cur_version = None
    cur_release = None
    cur_arch = None
    cur_version_release = None
    cur_source = None
    pkg_repo = None
    for info_line in info_output:
        # print(info_line)
        try:
            info_key, info_value = info_line.rstrip('\n').split(": ")
            info_key = info_key.rstrip(" ")
        except:
            continue

        
        # if info_key == "Version":
        #     print("-" * 30)
        #     print(package_name)
        #     cur_version = info_value
        # print(info_key, info_value)
        # continue

        if info_key == "Version":
            cur_version = info_value
        elif info_key == "Release":
            cur_release = info_value
            cur_version_release = f'{cur_version}-{cur_release}'
            if cur_version_release not in versions_info:
                versions_info[cur_version_release] = {
                    "version": cur_version_release
                }
        elif info_key == "Architecture":
            cur_arch = info_value
            if "architecture" not in versions_info[cur_version_release]:
                versions_info[cur_version_release]["architecture"] = info_value
            elif info_value not in versions_info[cur_version_release]["architecture"]:
                versions_info[cur_version_release]["architecture"] += " " + info_value
        elif info_key == "Size":
            if "size" not in versions_info[cur_version_release] or cur_arch == "x86_64":
                size = convert_size_to_kBs(info_value)
                if size is not None:
                    versions_info[cur_version_release]["size"] = size
        elif info_key == "Source":
            cur_source = info_value
            if distro.startswith("Fedora"):
                binary_URL = f'{distro_archives_URL}/{package_name}/{cur_version}/{cur_release}/src/{cur_source}'
                versions_info[cur_version_release]["binary_URL"] = binary_URL
            elif distro.startswith("CentOS"):
                versions_info[cur_version_release]["binary_URL"] = cur_source
        elif info_key == "Repository" or info_key == "From repo":
            if info_value in centOS_repos and distro.startswith("CentOS"):
                pkg_repo = info_value
        elif info_key not in info_to_parse or info_to_parse[info_key] in info:
            continue
        else:
            info[info_to_parse[info_key]] = info_value

    # return
    # print("/" * 35)
    pkg_homepage = info.get("homepage", "")
    if distro.startswith("Fedora"):
        repo_URL, maintainer = extract_package_info_from_distro_repo(distro_repos_URL, package_name)
        if repo_URL and maintainer:
            info["repo_URL"] = repo_URL
            info["maintainer"] = maintainer
            return info, versions_info

        pkg_base_name = extract_base_package_name(package_name)
        repo_URL, maintainer = extract_package_info_from_distro_repo(distro_repos_URL, pkg_base_name)
        if repo_URL and maintainer:
            info["repo_URL"] = repo_URL
            info["maintainer"] = maintainer
            fix_package_versions_binary_URLs(pkg_base_name, package_name, versions_info)
            return info, versions_info

        if pkg_homepage.startswith("https://github.com/"): #fallback to github repo (if existant)
            info["repo_URL"] = pkg_homepage
            fix_package_versions_binary_URLs(pkg_base_name, package_name, versions_info)
            pkg_repo_id = extract_package_repo_id(pkg_homepage, "https://github.com/")
            maintainer = extract_package_info_from_github_repo(pkg_repo_id)
            if maintainer:
                info["maintainer"] = maintainer

        return info, versions_info

    if distro.startswith("CentOS"):
        if pkg_repo is not None:
            binary_base_URL = f'{distro_archives_URL}/{centOS_repos[pkg_repo]}/Source/SPackages/'
            for vers_key, vers_info in versions_info.items():
                versions_info[vers_key]["binary_URL"] = binary_base_URL + vers_info["binary_URL"]
        else:
            for vers_key, vers_info in versions_info.items():
                versions_info[vers_key].pop("binary_URL", None)

        if pkg_homepage.startswith("https://github.com/"):
            info["repo_URL"] = pkg_homepage
            pkg_repo_id = extract_package_repo_id(pkg_homepage, "https://github.com/")
            maintainer = extract_package_info_from_github_repo(pkg_repo_id)
            if maintainer:
                info["maintainer"] = maintainer
                return info, versions_info

        maintainer = extract_package_info_from_distro_repo2(distro_repos_URL, package_name)
        if maintainer:
            info["repo_URL"] = distro_repos_URL.replace("/api/0/", "/") + "/" + package_name
            info["maintainer"] = maintainer
            return info, versions_info

        pkg_base_name = extract_base_package_name(package_name)
        maintainer = extract_package_info_from_distro_repo2(distro_repos_URL, pkg_base_name)
        if maintainer:
            info["repo_URL"] = distro_repos_URL.replace("/api/0/", "/") + "/" + pkg_base_name
            info["maintainer"] = maintainer

    return info, versions_info


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
        return res_data[0]
    except:
        pass

    return None


def add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, package_id):
    if len(pkg_versions_to_add) == 0:
        return False

    try:
        res = JWTAuth_obj.session.post(f'{base_URL}/packages/{package_id}/versions/', json=pkg_versions_to_add)
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
    package_info["type"] = "rpm"

    # print("package_info: ", package_info)

    try:
        res = JWTAuth_obj.session.post(f'{base_URL}/packages/', json=package_info)
        if res.status_code == 201:
            return True
        print("status: ", res.status_code, res.json())
    except:
        pass

    return False
    

@ray.remote
def parallel_processing(distro, base_URL, package_name, distro_archives_URL, distro_repos_URL, i):
    # print(f"-> Now processing package: '{package_name}' - #{i}")
    report_msg = f"-> Package #{i} - {package_name}: "
    pkg_existing_info = fetch_package_info(distro, base_URL, package_name)

    if pkg_existing_info is None: # package not included
        package_info, package_versions = extract_package_info(package_name, distro, distro_archives_URL, distro_repos_URL)
        # print("--->", package_name)
        # print(package_info, "\n")
        # print(package_versions, "\n", "-" *30)
        # return
        pkg_versions_to_add = []
        for pkg_version_info in package_versions.values():
            pkg_versions_to_add.append({
                **pkg_version_info
            })

        package_saved_flag = add_new_package(distro, base_URL, package_name, package_info, pkg_versions_to_add)
        if package_saved_flag:
            report_msg += "successfully added"
        else:
            report_msg += "failed to be added"
    else: # package is included not need to re-parse its core info
        pkg_existing_versions = get_package_existing_versions(pkg_existing_info['versions'])
        package_versions = extract_package_version_names(package_name)

        pkg_versions_to_add = []
        for pkg_version, pkg_version_info in package_versions.items():
            if pkg_version in pkg_existing_versions:
                continue

            # new version
            pkg_version_arch, pkg_version_size, pkg_version_repo = extract_package_version_info(pkg_version_info["full_name"])
            if distro.startswith("Fedora"):
                pkg_version_binary_URL = f'{distro_archives_URL}/{package_name}/{pkg_version_info["name"]}/{pkg_version_info["release"]}/src/{pkg_version_info["full_name"]}.src.rpm'
            elif distro.startswith("CentOS") and pkg_version_repo:
                pkg_version_binary_URL = f'{distro_archives_URL}/{centOS_repos[pkg_version_repo]}/Source/SPackages/{pkg_version_info["full_name"]}.src.rpm'
            else:
                pkg_version_binary_URL = ''

            pkg_versions_to_add.append({
                "version": pkg_version,
                "architecture": pkg_version_arch,
                "size": pkg_version_size,
                "binary_URL": pkg_version_binary_URL
            })

        new_versions_flag = add_new_versions_to_existing_package(base_URL, pkg_versions_to_add, pkg_existing_info["id"]) # add only the possible new versions
        if new_versions_flag:
            report_msg += "successfully added new versions "
        else:
            report_msg += "no new version was added "

    return report_msg


class JWTAuth:

    def __init__(self, user, password, base_URL):
        self.base_URL = base_URL
        self.user, self.password = user, password

        self._session = requests.Session()  # Session for tokens
        self.authenticate()

        self.session = requests.Session()  # Authenticated session
        self.session.auth = self.auth
        self.session.hooks['response'].append(self.reauth)

    def auth(self, req):
        """Just set the authentication token, on every request."""
        req.headers['Authorization'] = f'Bearer {self.access}'
        return req

    def reauth(self, res, *args, **kwargs):
        """Hook to re-authenticate whenever authentication expires."""
        if res.status_code == 403: #access forbiden
            if res.request.headers.get('REATTEMPT'):
                res.raise_for_status()
            self.refresh_auth()
            req = res.request
            req.headers['REATTEMPT'] = 1
            req = self.session.auth(req)
            res = self.session.send(req)
            return res

    def refresh_auth(self):
        """Use the refresh token to get a new access token."""
        payload = {
            "refresh": self.refresh
        }
        res = self._session.post(f'{self.base_URL}/users/login/token/refresh/', data=payload)
        if res.status_code == 200:
            self.refresh, self.access = res.json()['refresh'], res.json()['access']
        else:
            # Token expired -> re-authenticate
            self.authenticate()

    def authenticate(self):
        payload = {
            "username": self.user,
            "password": self.password
        }
        res = self._session.post(f'{self.base_URL}/users/login/', data=payload)
        res.raise_for_status()
        data = res.json()
        self.refresh, self.access = data['refresh'], data['access']

    def rm_token(self):
        payload = {
            "refresh_token": self.refresh
        }
        self._session.post(f'{self.base_URL}/users/logout/', data=payload)


if __name__ == "__main__":
    cmdParser = argparse.ArgumentParser(
        allow_abbrev=False, 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A script that parses useful info about all software packages (along with all their corresponding available versions) of a Linux distribution, that uses the 'dnf' package manager, and sends them to a backend through an API in order to be saved in a database",
        epilog='''for example in order to parse info about the Fedora packages (given the fact that the backend runs on the same machine):
$ python3 dnf_collector.py -d Fedora -u http://localhost:8000/api/v1 -a https://kojipkgs.fedoraproject.org/packages -r https://src.fedoraproject.org/api/0/rpms
you should have also set the environment variables: GITHUB-TOKEN and USERNAME, PASSWORD (credentials to access the backend API)
'''
)
    cmdParser.add_argument('--max-concurrency', '-c', type=int, dest='max_concurrency', metavar='<int>', help='[default: 50] Number of maximum packages that will be processed concurrently', default=50)
    cmdParser.add_argument('--distro', '-d', type=str, dest='distro', metavar='<str>', help='The linux distribution name', required=True)
    cmdParser.add_argument('--API-URL', '-u', type=str, dest='base_URL', metavar='<url>', help="Backend's API base URL", required=True)
    cmdParser.add_argument('--archives-url', '-a', type=str, dest='distro_archives_URL', metavar='<url>', help="Linux distribution's archives base URL", required=True)
    cmdParser.add_argument('--repos-url', '-r', type=str, dest='distro_repos_URL', metavar='<url>', help="Linux distribution's repositories base URL", required=True)

    cmdArgs = vars(cmdParser.parse_args())

    info_output = (os.popen(f'lsb_release -r')).readline()
    distro_release = info_output.rstrip("\n").split("Release:")[1].lstrip("\t")
    distro = f"{cmdArgs['distro']}:{distro_release}"

    print("--> Linux Package Collector started..")
    print('-> Command line arguments:')
    print('- Linux Distribution:', distro)
    print("- Backend's API base URL:", cmdArgs['base_URL'])
    print("- Linux distribution's archives base URL:", cmdArgs['distro_archives_URL'])
    print("- Linux distribution's repositories base URL:", cmdArgs['distro_repos_URL'])
    print('- Number of maximum packages to be processed concurrently:', cmdArgs['max_concurrency'])
    print("-" * 35)

    JWTAuth_obj = JWTAuth(getenv('USERNAME'), getenv('PASSWORD'), cmdArgs['base_URL'])
    parse_packages_info(distro, cmdArgs['base_URL'], cmdArgs['max_concurrency'], cmdArgs['distro_archives_URL'], cmdArgs['distro_repos_URL'])
    print("--> Linux Package Collector finished..")
    JWTAuth_obj.rm_token()
    # print(info_output)
    # print("\n" * 4)
    # info_output = (os.popen(f'dnf info firefox')).readlines()
    # print(info_output)

    # info_output = (os.popen(f'dnf info cracklib | grep -wE "^Source"')).readlines()


    # for info in info_output:
    #     print(info)
    # s, b = extract_package_version_info("accountsservice", "0.6.55-0ubuntu12~20.04.5", cmdArgs['distro_archives_URL'])
    # print(s, b)
    # s, b = extract_package_version_info("accountsservice", "0.6.55-0ubuntu12~20.04.5", cmdArgs['distro_archives_URL'])
    # print(s, b)
    # data = load_package_licenses_file("pkgs_licenses.json")
    # print(data)
    # license, repo = extract_package_license_from_salsa("http://archive.ubuntu.com/ubuntu/pool/universe/r/redis/redis_5.0.7-2_all.deb")
    # print("license:", license)
    # print("repo:", repo)
    # lc = extract_package_license_from_github_repo("https://github.com/andymccurdy/redis-py")
    # print(lc)

