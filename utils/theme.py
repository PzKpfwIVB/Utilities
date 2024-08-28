""" A module for setting a pre-defined theme to Qt objects. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.1.0'

# Built-in modules
from dataclasses import dataclass, field, fields
import json
import os
import sys

# Qt6 modules
from PySide6.QtGui import *


WidgetTheme: _WidgetTheme | None = None


@dataclass
class _ThemeParameters:
    """ Dataclass for storing the palette parameter values to
    a given theme (to LIGHT, by default). """

    src_file: str | None = None
    Window: QColor = field(init=False)
    WindowText: QColor = field(init=False)
    Base: QColor = field(init=False)
    AlternateBase: QColor = field(init=False)
    ToolTipBase: QColor = field(init=False)
    ToolTipText: QColor = field(init=False)
    Text: QColor = field(init=False)
    Button: QColor = field(init=False)
    ButtonText: QColor = field(init=False)
    BrightText: QColor = field(init=False)
    Link: QColor = field(init=False)
    Highlight: QColor = field(init=False)
    HighlightedText: QColor = field(init=False)

    def __post_init__(self):
        """ Defining the default colours. """

        if self.src_file is None:
            self.src_file = './themes/LIGHT.json'

        with open(self.src_file, 'r') as f:
            data = json.load(f)

        for key, value in data.items():
            setattr(self, key, QColor(value['r'], value['g'], value['b']))

    def write_json(self, destination) -> None:
        """ Writes the content to a JSON file.

        Parameters
        ----------
        destination : str
            Path where the file should be written.
        """

        dict_repr = {f.name: {'r': getattr(self, f.name).red(),
                              'g': getattr(self, f.name).green(),
                              'b': getattr(self, f.name).blue()}
                     for f in fields(self) if f.name != 'src_file'}

        with open(destination, 'w') as f:
            f.write(json.dumps(dict_repr, indent=4))


class _WidgetTheme:
    """ A class for Enum-like access to themes. """

    def __init__(self):
        """ Initializer for the class. """

        self._theme_dict = {f.split('.')[0]: _ThemeParameters(f'./themes/{f}')
                            for f in os.listdir('./themes') if '.json' in f}

    def __getattr__(self, name):
        return self._theme_dict[name]

    @classmethod
    def _stub_repr(cls) -> str:
        """ Helper class method for stub file creation. """

        repr_ = f"class {cls.__name__}:\n"
        repr_ += '\n'.join([f"\t{f.split('.')[0]} = None"
                            "  # type: _ThemeParameters"
                            for f in os.listdir('./themes') if '.json' in f])

        return repr_


def set_widget_theme(widget, theme) -> None:
    """ Sets a QWidget's palette to values defined by the theme.

    Parameters
    ----------
    widget : QWidget
        A widget whose palette is to be set to the requested theme.

    theme : WidgetTheme
        The theme to set for the widget.
    """

    palette = QPalette()
    for cr in QPalette.ColorRole:
        if (value := getattr(theme.value, cr.name, None)) is not None:
            palette.setColor(QPalette.ColorRole[cr.name], value)

    widget.setPalette(palette)


def _init_module() -> None:
    """ Initializes the module. """

    if not os.path.exists('./theme.pyi'):
        repr_ = _WidgetTheme._stub_repr()
        repr_ += "\n\nWidgetTheme = None  # type: _WidgetTheme\n\n"
        repr_ += "def set_widget_theme(widget, theme): ..."

        with open('./theme.pyi', 'w') as f:
            f.write(repr_)

    global WidgetTheme
    if WidgetTheme is None:
        WidgetTheme = _WidgetTheme()


_init_module()


if __name__ == '__main__':
    pass
