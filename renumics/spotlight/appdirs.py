"""
Module managing different application directories (config, cache, temp,...)
"""

from pathlib import Path
import appdirs

_APP_NAME = "spotlight"
_APP_AUTHOR = "renumics"

config_dir = Path(appdirs.user_config_dir(_APP_NAME, _APP_AUTHOR))
cache_dir = Path(appdirs.user_cache_dir(_APP_NAME, _APP_AUTHOR))
