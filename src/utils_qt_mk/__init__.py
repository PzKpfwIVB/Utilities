import os

_PACKAGE_DIR = os.path.dirname(__file__)
_DEFAULT_THEME_DIR = os.path.join(os.path.dirname(__file__), 'themes')

# Fallback for development
if not os.path.exists(_DEFAULT_THEME_DIR):
    src_path = _DEFAULT_THEME_DIR
    for _ in range(5):
        src_path, _ = os.path.split(src_path)

    src_path = os.path.join(src_path, 'src', 'utils_qt_mk', 'themes')
    if os.path.exists(src_path):
        _DEFAULT_THEME_DIR = src_path

_THEME_DIR = _DEFAULT_THEME_DIR


def set_theme_dir(new_path: str):
    """ Sets a path to the theme directory enabling the use of the Theme module
    and other reliant modules.

    :param new_path: The path to the directory containing themes.
    """

    global _THEME_DIR
    _THEME_DIR = new_path


def get_theme_dir():
    """ Returns the currently set path to the directory containing themes. """

    return _THEME_DIR
