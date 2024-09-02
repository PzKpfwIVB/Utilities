from dataclasses import dataclass

PathTypes = None  # type: _PathTypes

@dataclass
class PathData:
	path_id : str
	window_title : str
	dialog_type : int
	file_type_filter : str
	path : str

	def __init__(self, path_id: str, window_title: str, dialog_type: int, file_type_filter: str, path: str): ...

	@property
	def as_dict(self) -> dict: ...

class _PathTypes:
	destination_themes = None  # type: PathData

def custom_dialog(parent, path_data, custom_title=None) -> tuple[bool, str | None]: ...