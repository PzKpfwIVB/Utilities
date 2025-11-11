from __future__ import annotations
from dataclasses import dataclass, field, fields
import json
import os
from typing import TypeVar
from PySide6.QtGui import *
from PySide6.QtWidgets import QWidget
from utils_qt_mk.config import _PACKAGE_DIR, _STUBS_DIR, theme_dir
from utils_qt_mk.general import Singleton, get_imports, get_functions, get_classes, stub_repr


WidgetTheme: _WidgetTheme = None
QWidgetT = TypeVar('QWidgetT', bound=QWidget)


def get_theme_types(fetch_data: bool = False) -> list[str | ThemeParameters]: ...
def set_widget_theme(widget: QWidgetT, theme: ThemeParameters = None) -> None: ...
def write_stub() -> None: ...


@dataclass
class ThemeParameters:
	def __init__(self, src_file: str | None = None) -> None: ...
	def write_json(self, destination: str) -> None: ...


class _WidgetTheme(metaclass=Singleton):
	dark: ThemeParameters = None
	light: ThemeParameters = None
	matrix: ThemeParameters = None
	yellow: ThemeParameters = None
	def __init__(self) -> None: ...
	def load_dict(self) -> None: ...
