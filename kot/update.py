import requests

import kot

from .console import log


def latest():
    """Return useful data about the latest version."""
    try:
        latest_http = requests.get("https://api.github.com/repos/andreasxp/kot/releases/latest", timeout=1)
        latest_http.raise_for_status()

        data = latest_http.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError("Could not retrieve latest version") from e

    version = data["tag_name"]
    link = data["zipball_url"]

    return version, link


def prompt_to_update():
    """If an update is available, prompt to update."""
    try:
        version, link = latest()
    except ConnectionError:
        return

    if kot.__version__ < version:
        log(f"Version {version} available. Update by running:\n  pip install --upgrade {link}")
