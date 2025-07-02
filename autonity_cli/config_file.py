"""
Configuration file location and definition.
"""

from __future__ import annotations

import os
import os.path
from configparser import ConfigParser
from typing import Any, Mapping, Optional

from .logging import log

# pylint: disable=global-statement


class ConfigFile:
    """
    Wrap a config file section, adding the ability to query a relative path
    """

    _section: Mapping[str, Any]

    def __init__(self, section: Mapping[str, Any]):
        self._section = section

    def get(self, attribute: str) -> Optional[str]:
        """
        String attribute
        """
        return self._section.get(attribute)

    def get_path(self, attribute: str) -> Optional[str]:
        """
        For a path attribute, return the full path supporting tilda,
        absolute paths, or paths relative to the config file
        directory.  E.g. if a config file with path `../.autrc`
        contains an attribute with value `somedir/somefile`, return
        the absolute path of `../somedir/somefile`.
        """
        attr_path = self._section.get(attribute)
        if attr_path:
            # Handle ~
            attr_path = os.path.expanduser(attr_path)

            # If an absolute path was given, return as-is.  Else make
            # the path relative to the config file location
            # `config_file_dir` (which is set when the config file is
            # first discovered).

            if os.path.isabs(attr_path):
                return os.path.normpath(attr_path)

            return os.path.normpath(os.path.join(config_file_dir, attr_path))

        return None


CONFIG_FILE_NAME = ".autrc"
"""
Search current and parent directories for this file.
"""

DOT_CONFIG_FILE_NAME = "autrc"
"""
Check for this file in the ~/.config/aut directory.
"""

CONFIG_FILE_SECTION_NAME = "aut"

config_file_data: ConfigFile = ConfigFile({})

config_file_dir: str = "."

config_file_cached = False


def _find_config_file() -> str | None:
    """
    Find the config file in the file system.  For now, find the first
    .autrc file in the current or any parent dir.
    """

    home_dir = os.path.expanduser("~")

    # Start at
    cur_dir = os.getcwd()

    while True:
        config_path = os.path.join(cur_dir, CONFIG_FILE_NAME)
        if os.path.exists(config_path):
            log(f"found config file: {config_path}")
            return config_path

        # If/when we reach the home directory, check also for ~/.config/aut/autrc
        if cur_dir == home_dir:
            config_path = os.path.join(home_dir, ".config", "aut", DOT_CONFIG_FILE_NAME)
            if os.path.exists(config_path):
                log(f"HOME dir. found {config_path}")
                return config_path

            log(f"HOME dir. no file {config_path}")

        parent_dir = os.path.normpath(os.path.join(cur_dir, ".."))
        if parent_dir == cur_dir:
            log(f"reached root. no {CONFIG_FILE_NAME} file found")
            break

        cur_dir = parent_dir

    return None


def get_config_file() -> ConfigFile:
    """
    Load (and cache in memory) the first config file found.  If no
    config file is found, the empty dictionary is returned.
    """

    global config_file_dir
    global config_file_data
    global config_file_cached

    if not config_file_cached:
        config_file_path = _find_config_file()
        if config_file_path:
            config = ConfigParser()
            config.read(config_file_path)
            config_file_dir = os.path.dirname(config_file_path)
            config_file_data = ConfigFile(config[CONFIG_FILE_SECTION_NAME])

        config_file_cached = True

    return config_file_data
