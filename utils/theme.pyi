from dataclasses import dataclass

@dataclass
class ThemeParameters:
	def __init__(self, src_file: str=None): ...

	def write_json(self, destination) -> None: ...

class _WidgetTheme:
	dark = None  # type: ThemeParameters
	light = None  # type: ThemeParameters
	matrix = None  # type: ThemeParameters
	yellow = None  # type: ThemeParameters

	def load_dict(self) -> None: ...

WidgetTheme = None  # type: _WidgetTheme

def set_widget_theme(widget, theme): ...