class ThemeParameters: ...

class _WidgetTheme:
	dark = None  # type: _ThemeParameters
	light = None  # type: _ThemeParameters
	matrix = None  # type: _ThemeParameters

WidgetTheme = None  # type: _WidgetTheme

def set_widget_theme(widget, theme): ...