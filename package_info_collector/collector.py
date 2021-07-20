import os
import ray
import json
import requests
import random


info_to_parse = set(["Version", "Section", "Installed-Size", "Homepage", "Description", "Original-Maintainer"])


@ray.remote
class Packages:
    def __init__(self):
        self._packages = {}
        self._versions_SWHID_cache = {}

    def add(self, name, i):
        if name in self._packages:
            return False
        else:
            self._packages[name] = {
                "id": i,
                "Info": {},
                "Versions": {}
            }
            return True

    def exists(self, name):
        return name in self._packages

    def _get_hash_version_id(self, name, version):
        pkg_homepage = self._packages[name]["Info"].get("Homepage", version)
        pkg_section = self._packages[name]["Info"].get("Section", "")
        pkg_maintainer = self._packages[name]["Info"].get("Original-Maintainer", "")
        return version + pkg_homepage + pkg_maintainer + pkg_section

    def set_info(self, name, info):
        self._packages[name]["Info"] = info

    def set_version(self, name, version, arch):
        if version in self._packages[name]["Versions"]:
            self._packages[name]["Versions"][version]["arch"] = ["amd64", "i386"]
            return False # no need to re-calculate version's SWHID
        else:
            self._packages[name]["Versions"][version] = {
                "arch": [],
                "SWHID": None,
                "exists": None
            }
            if arch == "all":
                self._packages[name]["Versions"][version]["arch"] = ["amd64", "i386"]
            else:
                self._packages[name]["Versions"][version]["arch"] = [arch]

            hash_version_id = self._get_hash_version_id(name, version)
            if hash_version_id not in self._versions_SWHID_cache:
                return True 

            SWHID = self._versions_SWHID_cache[hash_version_id]["SWHID"]
            SWHID_exists = self._versions_SWHID_cache[hash_version_id]["exists"]
            self.set_version_SWHID(name, version, SWHID, SWHID_exists, False)
            return False

    def set_version_SWHID(self, name, version, SWHID, exists, set_cache_flag = True):
        self._packages[name]["Versions"][version]["SWHID"] = SWHID
        self._packages[name]["Versions"][version]["exists"] = exists

        if not set_cache_flag:
            return

        hash_version_id = self._get_hash_version_id(name, version)
        self._versions_SWHID_cache[hash_version_id] = {
            "SWHID": SWHID,
            "exists": exists
        }

    def get(self):
        return self._packages

    def dump(self):
        self._logs = open("packages.json", "w")
        json.dump(self._packages, self._logs, sort_keys=True, ensure_ascii=False, indent=4)
        self._logs.close()


def parse_packages_info():
    start_time = time.time()
    packages_output = (os.popen('apt list --all-versions')).readlines()
    random.shuffle(packages_output)
    print("Number of packages found:", (len(packages_output) // 2)-1)
    ray_ids = []
    ray.init()
    packages_obj = Packages.remote()
    pkg_counter = 0
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
        pkg_name, pkg_i = ray.get(finished)
        print(f"-> Package #{pkg_i} - {pkg_name} collected")

    packages = ray.get(packages_obj.get.remote())
    print("Number of packages parsed: ", len(packages))
    with open('packages_all.json', 'w') as f:
        json.dump(packages, f, sort_keys=True, ensure_ascii=False, indent=4)

    end_time = time.time() 
    print('-> Elapsed time: ', end_time - start_time)

def parse_package_version(package_name, string, packages):
    splitted_package_version = string.split(" ")
    package_version = splitted_package_version[1]
    package_arch = splitted_package_version[2]
    calc_SWHID_flag = ray.get([packages.set_version.remote(package_name, package_version, package_arch)])[0]
    return calc_SWHID_flag, package_version
    

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


def SWHID_resolve(SWHID, package_name, package_version, packages):
    if SWHID == None:
        return
        
    exists = None
    try:
        response = requests.get('https://archive.softwareheritage.org/api/1/resolve/' + SWHID)
        if response.status_code == 200:
            exists = True
        elif response.status_code == 404:
            exists = False
    except:
        pass
        
    packages.set_version_SWHID.remote(package_name, package_version, SWHID, exists)
    

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


@ray.remote
def parallel_processing(line, packages, i):
    package_name, splitted_line = line.split("/")
    print(f"package: '{package_name}'")
    parse_info_flag = ray.get([packages.add.remote(package_name, i)])[0]
    if parse_info_flag:
        parse_package_info(package_name, packages)

    calc_SWHID_flag, package_version = parse_package_version(package_name, splitted_line, packages)
    if calc_SWHID_flag:
        SWHID = calc_SWHID(package_name, package_version)
        SWHID_resolve(SWHID, package_name, package_version, packages)
 
    packages.dump.remote()


if __name__ == "__main__":
    print("started")
    parse_packages_info()
