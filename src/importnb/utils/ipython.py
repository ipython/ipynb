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
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    if "InteractiveShellApp" not in config:
        config["InteractiveShellApp"] = {}

    if "extensions" not in config["InteractiveShellApp"]:
        config["InteractiveShellApp"]["extensions"] = []

    return config, location


def install(ip=None):
    config, location = load_config()

    if "importnb" not in config["InteractiveShellApp"]["extensions"]:
        config["InteractiveShellApp"]["extensions"].append("importnb")

    with location.open("w") as file:
        json.dump(config, file)

    print("""🤘 Rock on!  You can import notebooks in your notebooks.""")


def installed():
    config = load_config()
    return "importnb" in config.get("InteractiveShellApp", {}).get("extensions", [])


def uninstall(ip=None):
    config, location = load_config()

    config["InteractiveShellApp"]["extensions"] = [
        ext
        for ext in config["InteractiveShellApp"]["extensions"]
        if ext != "importnb.utils.ipython"
    ]

    with location.open("w") as file:
        json.dump(config, file)


if __name__ == "__main__":
    from importnb.utils.export import export

    export("ipython.ipynb", "../../utils/ipython.py")
