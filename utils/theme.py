""" A module for setting a pre-defined theme to Qt objects. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.1.3'

# Built-in modules
from dataclasses import dataclass, field, fields
import json
import os

# Qt6 modules
from PySide6.QtGui import *
from PySide6.QtWidgets import QWidget

# Custom modules
from utils._general import Singleton, stub_repr


WidgetTheme: _WidgetTheme | None = None


@dataclass
class ThemeParameters:
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
    Highlight: QColor = field(init=False)
    HighlightedText: QColor = field(init=False)

    def __post_init__(self):
        """ Defining the default colours. """

        if self.src_file is None:
            self.src_file = 'themes/light.json'

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


class _WidgetTheme(metaclass=Singleton):
    """ A class for Enum-like access to themes. """

    def __init__(self):
        """ Initializer for the class. """

        self._theme_dict = None
        self.load_dict()  # For dynamic access to themes

    def __getattr__(self, name):
        return self._theme_dict[name]

    def load_dict(self):
        """ Loads the content of theme JSONs into the internal dictionary. """

        self._theme_dict = {f.split('.')[0]: ThemeParameters(f'./themes/{f}')
                            for f in os.listdir('./themes') if '.json' in f}

    # @classmethod
    # def _stub_repr(cls) -> str:
    #     """ Helper class method for stub file creation. """
    #
    #     repr_ = f"class {cls.__name__}:\n"
    #     repr_ += '\n'.join([f"\t{f.split('.')[0]} = None"
    #                         "  # type: ThemeParameters"
    #                         for f in os.listdir('./themes') if '.json' in f])
    #     repr_ += "\n\n\tdef load_dict(self) -> None: ..."
    #
    #     return repr_


def set_widget_theme(widget: QWidget, theme: ThemeParameters = None) -> None:
    """ Sets a QWidget's palette to values defined by the theme.

    Parameters
    ----------
    widget : QWidget
        A widget whose palette is to be set to the requested theme.

    theme : ThemeParameters, optional
        The theme to set for the widget. The default is None, which makes the
        function try to read the set theme property of the widget.
    """

    if theme is None:
        theme = widget.theme  # Raise the error properly if no theme is provided

    disabled = "Button ButtonText WindowText Text".split()  # 'Light' omitted

    palette = QPalette()
    for cr in QPalette.ColorRole:
        if (colour := getattr(theme, cr.name, None)) is not None:
            palette.setColor(QPalette.ColorRole[cr.name], colour)
            if cr.name in disabled:
                palette.setColor(QPalette.Disabled, QPalette.ColorRole[cr.name],
                                 colour.darker())

    widget.setPalette(palette)


def _init_module() -> None:
    """ Initializes the module. """

    if not os.path.exists('./theme.pyi'):
        reprs = [stub_repr(set_widget_theme), '\n\n']
        class_reprs = []
        classes = {ThemeParameters: None,
                   _WidgetTheme: None}
        for cls, sigs in classes.items():
            if cls == _WidgetTheme:
                extra_cvs = '\n'.join(
                    [f"\t{f.split('.')[0]}: ThemeParameters = None"
                     for f in os.listdir('./themes') if '.json' in f])
            else:
                extra_cvs = None

            class_reprs.append(
                stub_repr(cls, signals=sigs, extra_cvs=extra_cvs))

        reprs.append('\n\n'.join(class_reprs))

        repr_ = "from dataclasses import dataclass\n" \
                "from PySide6.QtWidgets import QWidget\n" \
                "from utils._general import Singleton\n\n\n" \
                "WidgetTheme: _WidgetTheme = None\n\n\n" \
                f"{''.join(reprs)}"

        with open('./theme.pyi', 'w') as f:
            f.write(repr_)

    global WidgetTheme
    WidgetTheme = _WidgetTheme()


_init_module()


if __name__ == '__main__':
    pass
