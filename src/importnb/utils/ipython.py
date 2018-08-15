# coding: utf-8
from IPython import paths, get_ipython

from pathlib import Path
import json, ast


def get_config():
    ip = get_ipython()
    return Path(ip.profile_dir.location if ip else paths.locate_profile()) / "ipython_config.json"


def load_config():
    location = get_config()
    try:
        with location.open() as file:
            config = json.load(file)
    except (FileNotFoundError, getattr(json, "JSONDecodeError", ValueError)):
        config = {}

    if "InteractiveShellApp" not in config:
        config["InteractiveShellApp"] = {}

    if "extensions" not in config["InteractiveShellApp"]:
        config["InteractiveShellApp"]["extensions"] = []

    return config, location


def install(project="importnb"):
    config, location = load_config()

    if not installed(project):
        config["InteractiveShellApp"]["extensions"].append(project)

    with location.open("w") as file:
        json.dump(config, file)

    print("""<3 {}""".format(project))


def installed(project):
    config, location = load_config()
    return project in config.get("InteractiveShellApp", {}).get("extensions", [])


def uninstall(project="importnb"):
    config, location = load_config()

    config["InteractiveShellApp"]["extensions"] = [
        ext for ext in config["InteractiveShellApp"]["extensions"] if ext != project
    ]

    with location.open("w") as file:
        json.dump(config, file)
    print("""</3 {}.""".format(project))


if __name__ == "__main__":
    from importnb.utils.export import export

    export("ipython.ipynb", "../../utils/ipython.py")
