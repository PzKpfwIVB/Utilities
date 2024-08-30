PathTypes = None  # type: _PathTypes

class PathData:
	path_id = None  # type: str
	window_title = None  # type: str
	dialog_type = None  # type: int
	file_type_filter = None  # type: str
	path = None  # type: str

class _PathTypes:
	destination_themes = None  # type: PathData

def custom_dialog(parent, path_data, custom_title=None) -> tuple[bool, str | None]: ...