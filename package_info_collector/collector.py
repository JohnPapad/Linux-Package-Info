import os
import sys


def collect_package_names():
    stream = os.popen('apt-cache search .')
    output = stream.readlines()
    print("Number of packages found: ", len(output))
    return output

def parse_packages_info(cmd_output):
    packages = {}
    counter = 0
    for i, line in enumerate(cmd_output):
        package_name = line.rstrip('\n').split(" - ")[0]
        print(f"package: '{package_name}'")

        versions = {}
        versions_output = (os.popen(f'apt-cache madison {package_name}')).readlines()
        for version_line in versions_output:
            _, version, arch = version_line.rstrip('\n').split(" | ")
            version = version.lstrip(" ")
            arch = arch.split(" ")[-2]
            assert arch == "amd64" or arch == "i386", "parsing error in package version's architecture"
            # print(f"version: '{version}' - '{arch}'")
            if version not in versions:
                versions[version] = set()

            versions[version].add(arch)

        packages[package_name] = {}
        packages[package_name]["versions"] = versions
           

if __name__ == "__main__":
    cmd_output = collect_package_names()
    parse_packages_info(cmd_output)
