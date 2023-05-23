"""
Requests-related helpers.
"""

from renumics.spotlight.__version__ import __version__

headers = {
    # https://meta.wikimedia.org/wiki/User-Agent_policy
    "User-Agent": f"SpotlightBot/{__version__} (https://spotlight.renumics.com/)"
}
