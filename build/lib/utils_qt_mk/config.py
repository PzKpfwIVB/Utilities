""" A module for setting up constants for the package. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

import os

_PACKAGE_DIR = os.path.dirname(__file__)
_DEFAULT_THEME_DIR = os.path.join(os.path.dirname(__file__), 'themes')

_CFD_DATA_FILE = os.path.join(_PACKAGE_DIR, 'custom_file_dialog_data.json')

_USE_THEME = True

# Fallback for development
if not os.path.exists(_DEFAULT_THEME_DIR):
    src_path = _DEFAULT_THEME_DIR
    for _ in range(5):
        src_path, _ = os.path.split(src_path)

    src_path = os.path.join(src_path, 'src', 'utils_qt_mk', 'themes')
    if os.path.exists(src_path):
        _DEFAULT_THEME_DIR = src_path

_THEME_DIR = _DEFAULT_THEME_DIR
_ICON_FILE_PATH = ''  # Resulting in the default icon


def theme_dir() -> str:
    """ Returns the currently set path to the directory containing themes. """

    return _THEME_DIR


def set_theme_dir(new_path: str) -> None:
    """ Sets a path to the theme directory enabling the use of the theme module
    and other reliant modules.

    :param new_path: The path to the directory containing themes.
    """

    global _THEME_DIR
    _THEME_DIR = new_path


def cfd_data_file_path() -> str:
    """
    Returns the currently set path to the file containing the custom file dialog
    data.
    """

    return _CFD_DATA_FILE


def set_cfd_data_file_path(new_path: str) -> None:
    """ Sets a new path for the custom file dialog data file.

    :param new_path: The new path to set.
    """

    global _CFD_DATA_FILE
    _CFD_DATA_FILE = new_path


def use_theme() -> bool:
    """ Returns the enabled state of the theme package. """

    return _USE_THEME


def set_use_theme(use: bool = True) -> None:
    """ Enables/disables the use of the theme package.

    :param use: The new state to set. The default is True.
    """

    global _USE_THEME
    _USE_THEME = use


def icon_file_path() -> str:
    """ Returns the path for the icon file to be used in the dialogs. """

    return _ICON_FILE_PATH


def set_icon_file_path(new_path: str = '') -> None:
    """ Sets the path for the icon file to be used in the dialogs.

    :param new_path: The new path to set for the windows. The default is an
        empty string, leading to the default icon.
    """

    global _ICON_FILE_PATH
    _ICON_FILE_PATH = new_path
