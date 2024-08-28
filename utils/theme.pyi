class _WidgetTheme:
	DARK = None  # type: _ThemeParameters
	LIGHT = None  # type: _ThemeParameters
	MATRIX = None  # type: _ThemeParameters

WidgetTheme = None  # type: _WidgetTheme

def set_widget_theme(widget, theme): ...