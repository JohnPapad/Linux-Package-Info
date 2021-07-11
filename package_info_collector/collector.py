import os
import ray
import sys
import json


info_to_parse = set(["Version", "Section", "Installed-Size", "Homepage", "Description", "Bugs"])

def parse_packages_info():
    packages_output = (os.popen('apt-cache search .')).readlines()
    print("Number of packages found: ", len(packages_output))

    ids = []
    ray.init()
    for line in packages_output:
        id = parallel_processing.remote(line)
        ids.append(id)

    packages = ray.get(ids)
    print("Number of packages parsed: ", len(packages))
    with open('data.json', 'w') as f:
        json.dump(packages, f)


@ray.remote
def parallel_processing(line):
    package_name = line.rstrip('\n').split(" - ")[0]
    print(f"package: '{package_name}'")
    package = {}
    package[package_name] = {}

    versions = {}
    versions_output = (os.popen(f'apt-cache madison {package_name}')).readlines()
    for version_line in versions_output:
        _, version, arch = version_line.rstrip('\n').split(" | ")
        version = version.lstrip(" ")
        arch = arch.split(" ")[-2]
        # assert arch == "amd64" or arch == "i386", "parsing error in package version's architecture"
        # print(f"version: '{version}' - '{arch}'")
        if version not in versions:
            versions[version] = set()

        versions[version].add(arch)

    for a, b in versions.items():
        versions[a] = list(b)

    package[package_name]["versions"] = versions

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

    package[package_name]["info"] = info

    return package


if __name__ == "__main__":
    parse_packages_info()
