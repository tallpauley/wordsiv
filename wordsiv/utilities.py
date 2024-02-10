from functools import lru_cache
import pkg_resources

# utilties
def installed_source_modules():
    packages = []
    for entry_point in pkg_resources.iter_entry_points("wordsiv_source_modules"):
        packages.append(entry_point.load())

    return packages
