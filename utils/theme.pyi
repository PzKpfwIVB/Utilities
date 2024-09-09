from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from utils._general import Singleton


WidgetTheme: _WidgetTheme = None


def set_widget_theme(widget: QWidget, theme: ThemeParameters = None) -> None: ...


@dataclass
class ThemeParameters:
	def __init__(self, src_file: str | None = None) -> None: ...
	def write_json(self) -> None: ...


class _WidgetTheme(metaclass=Singleton):
	dark: ThemeParameters = None
	light: ThemeParameters = None
	matrix: ThemeParameters = None
	yellow: ThemeParameters = None
	def __init__(self): ...
	def load_dict(self): ...
