from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QIcon, QKeyEvent, QMouseEvent, QPaintEvent
from PySide6.QtWidgets import QDialog, QMainWindow, QWidget
from utils._general import ReadOnlyDescriptor, Singleton


Colours: _Colours = None


def text_colour_threshold() -> int: ...
def set_text_colour_threshold(new_value: int) -> None: ...
def icon_file_path() -> str: ...
def set_icon_file_path(new_path: str = '') -> None: ...
def extended_default() -> bool: ...
def set_extended_default(new_default: bool) -> None: ...
def unlock_theme() -> None: ...


class Colour:
	b: ReadOnlyDescriptor = ReadOnlyDescriptor()
	g: ReadOnlyDescriptor = ReadOnlyDescriptor()
	name: ReadOnlyDescriptor = ReadOnlyDescriptor()
	r: ReadOnlyDescriptor = ReadOnlyDescriptor()

	def __init__(self, name: str = 'white', r: int = 255, g: int = 255, b: int = 255): ...
	@cached_property
	def as_hex(self) -> str: ...
	def as_qt(self, negative: bool = False) -> QColor: ...
	@cached_property
	def as_rgb(self) -> str: ...
	def colour_box(self, width: int = 20, height: int = 20) -> QIcon: ...
	def text_colour(self) -> Qt.GlobalColor: ...


class _Colours(metaclass=Singleton):
	aliceblue: Colour = None
	antiquewhite: Colour = None
	antiquewhite1: Colour = None
	antiquewhite2: Colour = None
	antiquewhite3: Colour = None
	antiquewhite4: Colour = None
	aquamarine: Colour = None
	aquamarine1: Colour = None
	aquamarine2: Colour = None
	aquamarine3: Colour = None
	aquamarine4: Colour = None
	azure: Colour = None
	azure1: Colour = None
	azure2: Colour = None
	azure3: Colour = None
	azure4: Colour = None
	beige: Colour = None
	bisque: Colour = None
	bisque1: Colour = None
	bisque2: Colour = None
	bisque3: Colour = None
	bisque4: Colour = None
	black: Colour = None
	blanchedalmond: Colour = None
	blue: Colour = None
	blue1: Colour = None
	blue2: Colour = None
	blue3: Colour = None
	blue4: Colour = None
	blueviolet: Colour = None
	brown: Colour = None
	brown1: Colour = None
	brown2: Colour = None
	brown3: Colour = None
	brown4: Colour = None
	burlywood: Colour = None
	burlywood1: Colour = None
	burlywood2: Colour = None
	burlywood3: Colour = None
	burlywood4: Colour = None
	cadetblue: Colour = None
	cadetblue1: Colour = None
	cadetblue2: Colour = None
	cadetblue3: Colour = None
	cadetblue4: Colour = None
	chartreuse: Colour = None
	chartreuse1: Colour = None
	chartreuse2: Colour = None
	chartreuse3: Colour = None
	chartreuse4: Colour = None
	chocolate: Colour = None
	chocolate1: Colour = None
	chocolate2: Colour = None
	chocolate3: Colour = None
	chocolate4: Colour = None
	coral: Colour = None
	coral1: Colour = None
	coral2: Colour = None
	coral3: Colour = None
	coral4: Colour = None
	cornflowerblue: Colour = None
	cornsilk: Colour = None
	cornsilk1: Colour = None
	cornsilk2: Colour = None
	cornsilk3: Colour = None
	cornsilk4: Colour = None
	cyan: Colour = None
	cyan1: Colour = None
	cyan2: Colour = None
	cyan3: Colour = None
	cyan4: Colour = None
	darkblue: Colour = None
	darkcyan: Colour = None
	darkgoldenrod: Colour = None
	darkgoldenrod1: Colour = None
	darkgoldenrod2: Colour = None
	darkgoldenrod3: Colour = None
	darkgoldenrod4: Colour = None
	darkgreen: Colour = None
	darkgrey: Colour = None
	darkkhaki: Colour = None
	darkmagenta: Colour = None
	darkolivegreen: Colour = None
	darkolivegreen1: Colour = None
	darkolivegreen2: Colour = None
	darkolivegreen3: Colour = None
	darkolivegreen4: Colour = None
	darkorange: Colour = None
	darkorange1: Colour = None
	darkorange2: Colour = None
	darkorange3: Colour = None
	darkorange4: Colour = None
	darkorchid: Colour = None
	darkorchid1: Colour = None
	darkorchid2: Colour = None
	darkorchid3: Colour = None
	darkorchid4: Colour = None
	darkred: Colour = None
	darksalmon: Colour = None
	darkseagreen: Colour = None
	darkseagreen1: Colour = None
	darkseagreen2: Colour = None
	darkseagreen3: Colour = None
	darkseagreen4: Colour = None
	darkslateblue: Colour = None
	darkslategrey: Colour = None
	darkslategrey1: Colour = None
	darkslategrey2: Colour = None
	darkslategrey3: Colour = None
	darkslategrey4: Colour = None
	darkturquoise: Colour = None
	darkviolet: Colour = None
	deeppink: Colour = None
	deeppink1: Colour = None
	deeppink2: Colour = None
	deeppink3: Colour = None
	deeppink4: Colour = None
	deepskyblue: Colour = None
	deepskyblue1: Colour = None
	deepskyblue2: Colour = None
	deepskyblue3: Colour = None
	deepskyblue4: Colour = None
	dimgrey: Colour = None
	dodgerblue: Colour = None
	dodgerblue1: Colour = None
	dodgerblue2: Colour = None
	dodgerblue3: Colour = None
	dodgerblue4: Colour = None
	firebrick: Colour = None
	firebrick1: Colour = None
	firebrick2: Colour = None
	firebrick3: Colour = None
	firebrick4: Colour = None
	floralwhite: Colour = None
	forestgreen: Colour = None
	gainsboro: Colour = None
	ghostwhite: Colour = None
	gold: Colour = None
	gold1: Colour = None
	gold2: Colour = None
	gold3: Colour = None
	gold4: Colour = None
	goldenrod: Colour = None
	goldenrod1: Colour = None
	goldenrod2: Colour = None
	goldenrod3: Colour = None
	goldenrod4: Colour = None
	grey: Colour = None
	grey0: Colour = None
	grey1: Colour = None
	grey2: Colour = None
	grey3: Colour = None
	grey4: Colour = None
	grey5: Colour = None
	grey6: Colour = None
	grey7: Colour = None
	grey8: Colour = None
	grey9: Colour = None
	grey10: Colour = None
	grey11: Colour = None
	grey12: Colour = None
	grey13: Colour = None
	grey14: Colour = None
	grey15: Colour = None
	grey16: Colour = None
	grey17: Colour = None
	grey18: Colour = None
	grey19: Colour = None
	grey20: Colour = None
	grey21: Colour = None
	grey22: Colour = None
	grey23: Colour = None
	grey24: Colour = None
	grey25: Colour = None
	grey26: Colour = None
	grey27: Colour = None
	grey28: Colour = None
	grey29: Colour = None
	grey30: Colour = None
	grey31: Colour = None
	grey32: Colour = None
	grey33: Colour = None
	grey34: Colour = None
	grey35: Colour = None
	grey36: Colour = None
	grey37: Colour = None
	grey38: Colour = None
	grey39: Colour = None
	grey40: Colour = None
	grey41: Colour = None
	grey42: Colour = None
	grey43: Colour = None
	grey44: Colour = None
	grey45: Colour = None
	grey46: Colour = None
	grey47: Colour = None
	grey48: Colour = None
	grey49: Colour = None
	grey50: Colour = None
	grey51: Colour = None
	grey52: Colour = None
	grey53: Colour = None
	grey54: Colour = None
	grey55: Colour = None
	grey56: Colour = None
	grey57: Colour = None
	grey58: Colour = None
	grey59: Colour = None
	grey60: Colour = None
	grey61: Colour = None
	grey62: Colour = None
	grey63: Colour = None
	grey64: Colour = None
	grey65: Colour = None
	grey66: Colour = None
	grey67: Colour = None
	grey68: Colour = None
	grey69: Colour = None
	grey70: Colour = None
	grey71: Colour = None
	grey72: Colour = None
	grey73: Colour = None
	grey74: Colour = None
	grey75: Colour = None
	grey76: Colour = None
	grey77: Colour = None
	grey78: Colour = None
	grey79: Colour = None
	grey80: Colour = None
	grey81: Colour = None
	grey82: Colour = None
	grey83: Colour = None
	grey84: Colour = None
	grey85: Colour = None
	grey86: Colour = None
	grey87: Colour = None
	grey88: Colour = None
	grey89: Colour = None
	grey90: Colour = None
	grey91: Colour = None
	grey92: Colour = None
	grey93: Colour = None
	grey94: Colour = None
	grey95: Colour = None
	grey96: Colour = None
	grey97: Colour = None
	grey98: Colour = None
	grey99: Colour = None
	grey100: Colour = None
	green: Colour = None
	green1: Colour = None
	green2: Colour = None
	green3: Colour = None
	green4: Colour = None
	greenyellow: Colour = None
	honeydew: Colour = None
	honeydew1: Colour = None
	honeydew2: Colour = None
	honeydew3: Colour = None
	honeydew4: Colour = None
	hotpink: Colour = None
	hotpink1: Colour = None
	hotpink2: Colour = None
	hotpink3: Colour = None
	hotpink4: Colour = None
	indianred: Colour = None
	indianred1: Colour = None
	indianred2: Colour = None
	indianred3: Colour = None
	indianred4: Colour = None
	ivory: Colour = None
	ivory1: Colour = None
	ivory2: Colour = None
	ivory3: Colour = None
	ivory4: Colour = None
	khaki: Colour = None
	khaki1: Colour = None
	khaki2: Colour = None
	khaki3: Colour = None
	khaki4: Colour = None
	lavender: Colour = None
	lavenderblush: Colour = None
	lavenderblush1: Colour = None
	lavenderblush2: Colour = None
	lavenderblush3: Colour = None
	lavenderblush4: Colour = None
	lawngreen: Colour = None
	lemonchiffon: Colour = None
	lemonchiffon1: Colour = None
	lemonchiffon2: Colour = None
	lemonchiffon3: Colour = None
	lemonchiffon4: Colour = None
	lightblue: Colour = None
	lightblue1: Colour = None
	lightblue2: Colour = None
	lightblue3: Colour = None
	lightblue4: Colour = None
	lightcoral: Colour = None
	lightcyan: Colour = None
	lightcyan1: Colour = None
	lightcyan2: Colour = None
	lightcyan3: Colour = None
	lightcyan4: Colour = None
	lightgoldenrod: Colour = None
	lightgoldenrod1: Colour = None
	lightgoldenrod2: Colour = None
	lightgoldenrod3: Colour = None
	lightgoldenrod4: Colour = None
	lightgoldenrodyellow: Colour = None
	lightgreen: Colour = None
	lightgrey: Colour = None
	lightpink: Colour = None
	lightpink1: Colour = None
	lightpink2: Colour = None
	lightpink3: Colour = None
	lightpink4: Colour = None
	lightsalmon: Colour = None
	lightsalmon1: Colour = None
	lightsalmon2: Colour = None
	lightsalmon3: Colour = None
	lightsalmon4: Colour = None
	lightseagreen: Colour = None
	lightskyblue: Colour = None
	lightskyblue1: Colour = None
	lightskyblue2: Colour = None
	lightskyblue3: Colour = None
	lightskyblue4: Colour = None
	lightslateblue: Colour = None
	lightslategrey: Colour = None
	lightsteelblue: Colour = None
	lightsteelblue1: Colour = None
	lightsteelblue2: Colour = None
	lightsteelblue3: Colour = None
	lightsteelblue4: Colour = None
	lightyellow: Colour = None
	lightyellow1: Colour = None
	lightyellow2: Colour = None
	lightyellow3: Colour = None
	lightyellow4: Colour = None
	limegreen: Colour = None
	linen: Colour = None
	magenta: Colour = None
	magenta1: Colour = None
	magenta2: Colour = None
	magenta3: Colour = None
	magenta4: Colour = None
	maroon: Colour = None
	maroon1: Colour = None
	maroon2: Colour = None
	maroon3: Colour = None
	maroon4: Colour = None
	mediumaquamarine: Colour = None
	mediumblue: Colour = None
	mediumorchid: Colour = None
	mediumorchid1: Colour = None
	mediumorchid2: Colour = None
	mediumorchid3: Colour = None
	mediumorchid4: Colour = None
	mediumpurple: Colour = None
	mediumpurple1: Colour = None
	mediumpurple2: Colour = None
	mediumpurple3: Colour = None
	mediumpurple4: Colour = None
	mediumseagreen: Colour = None
	mediumslateblue: Colour = None
	mediumspringgreen: Colour = None
	mediumturquoise: Colour = None
	mediumvioletred: Colour = None
	midnightblue: Colour = None
	mintcream: Colour = None
	mistyrose: Colour = None
	mistyrose1: Colour = None
	mistyrose2: Colour = None
	mistyrose3: Colour = None
	mistyrose4: Colour = None
	moccasin: Colour = None
	navajowhite: Colour = None
	navajowhite1: Colour = None
	navajowhite2: Colour = None
	navajowhite3: Colour = None
	navajowhite4: Colour = None
	navy: Colour = None
	navyblue: Colour = None
	oldlace: Colour = None
	olivedrab: Colour = None
	olivedrab1: Colour = None
	olivedrab2: Colour = None
	olivedrab3: Colour = None
	olivedrab4: Colour = None
	orange: Colour = None
	orange1: Colour = None
	orange2: Colour = None
	orange3: Colour = None
	orange4: Colour = None
	orangered: Colour = None
	orangered1: Colour = None
	orangered2: Colour = None
	orangered3: Colour = None
	orangered4: Colour = None
	orchid: Colour = None
	orchid1: Colour = None
	orchid2: Colour = None
	orchid3: Colour = None
	orchid4: Colour = None
	palegoldenrod: Colour = None
	palegreen: Colour = None
	palegreen1: Colour = None
	palegreen2: Colour = None
	palegreen3: Colour = None
	palegreen4: Colour = None
	paleturquoise: Colour = None
	paleturquoise1: Colour = None
	paleturquoise2: Colour = None
	paleturquoise3: Colour = None
	paleturquoise4: Colour = None
	palevioletred: Colour = None
	palevioletred1: Colour = None
	palevioletred2: Colour = None
	palevioletred3: Colour = None
	palevioletred4: Colour = None
	papayawhip: Colour = None
	peachpuff: Colour = None
	peachpuff1: Colour = None
	peachpuff2: Colour = None
	peachpuff3: Colour = None
	peachpuff4: Colour = None
	peru: Colour = None
	pink: Colour = None
	pink1: Colour = None
	pink2: Colour = None
	pink3: Colour = None
	pink4: Colour = None
	plum: Colour = None
	plum1: Colour = None
	plum2: Colour = None
	plum3: Colour = None
	plum4: Colour = None
	powderblue: Colour = None
	purple: Colour = None
	purple1: Colour = None
	purple2: Colour = None
	purple3: Colour = None
	purple4: Colour = None
	red: Colour = None
	red1: Colour = None
	red2: Colour = None
	red3: Colour = None
	red4: Colour = None
	rosybrown: Colour = None
	rosybrown1: Colour = None
	rosybrown2: Colour = None
	rosybrown3: Colour = None
	rosybrown4: Colour = None
	royalblue: Colour = None
	royalblue1: Colour = None
	royalblue2: Colour = None
	royalblue3: Colour = None
	royalblue4: Colour = None
	saddlebrown: Colour = None
	salmon: Colour = None
	salmon1: Colour = None
	salmon2: Colour = None
	salmon3: Colour = None
	salmon4: Colour = None
	sandybrown: Colour = None
	seagreen: Colour = None
	seagreen1: Colour = None
	seagreen2: Colour = None
	seagreen3: Colour = None
	seagreen4: Colour = None
	seashell: Colour = None
	seashell1: Colour = None
	seashell2: Colour = None
	seashell3: Colour = None
	seashell4: Colour = None
	sienna: Colour = None
	sienna1: Colour = None
	sienna2: Colour = None
	sienna3: Colour = None
	sienna4: Colour = None
	skyblue: Colour = None
	skyblue1: Colour = None
	skyblue2: Colour = None
	skyblue3: Colour = None
	skyblue4: Colour = None
	slateblue: Colour = None
	slateblue1: Colour = None
	slateblue2: Colour = None
	slateblue3: Colour = None
	slateblue4: Colour = None
	slategrey: Colour = None
	slategrey1: Colour = None
	slategrey2: Colour = None
	slategrey3: Colour = None
	slategrey4: Colour = None
	snow: Colour = None
	snow1: Colour = None
	snow2: Colour = None
	snow3: Colour = None
	snow4: Colour = None
	springgreen: Colour = None
	springgreen1: Colour = None
	springgreen2: Colour = None
	springgreen3: Colour = None
	springgreen4: Colour = None
	steelblue: Colour = None
	steelblue1: Colour = None
	steelblue2: Colour = None
	steelblue3: Colour = None
	steelblue4: Colour = None
	tan: Colour = None
	tan1: Colour = None
	tan2: Colour = None
	tan3: Colour = None
	tan4: Colour = None
	thistle: Colour = None
	thistle1: Colour = None
	thistle2: Colour = None
	thistle3: Colour = None
	thistle4: Colour = None
	tomato: Colour = None
	tomato1: Colour = None
	tomato2: Colour = None
	tomato3: Colour = None
	tomato4: Colour = None
	turquoise: Colour = None
	turquoise1: Colour = None
	turquoise2: Colour = None
	turquoise3: Colour = None
	turquoise4: Colour = None
	violet: Colour = None
	violetred: Colour = None
	violetred1: Colour = None
	violetred2: Colour = None
	violetred3: Colour = None
	violetred4: Colour = None
	wheat: Colour = None
	wheat1: Colour = None
	wheat2: Colour = None
	wheat3: Colour = None
	wheat4: Colour = None
	white: Colour = None
	whitesmoke: Colour = None
	yellow: Colour = None
	yellow1: Colour = None
	yellow2: Colour = None
	yellow3: Colour = None
	yellow4: Colour = None
	yellowgreen: Colour = None
	def __init__(self): ...
	def colour_at(self, idx: int) -> Colour: ...
	def from_qt(self, qc: QColor) -> Colour: ...
	def index(self, name: str) -> int: ...


@dataclass
class _ColourBoxData:
	def __init__(self, row: int = -1, column: int = -1, colour: Optional[Colour] = None) -> None: ...


class _ColourBoxDrawer(QWidget):
	colourSelected : ClassVar[Signal] = ...  # colourSelected(int)

	def __init__(self, default_colour: Colour): ...
	def keyPressEvent(self, event: QKeyEvent) -> None: ...
	def mousePressEvent(self, event: QMouseEvent) -> None: ...
	def paintEvent(self, event: QPaintEvent) -> None: ...
	@property
	def selection(self) -> Colour: ...
	@selection.setter
	def selection(self, new_selection: _ColourBoxData) -> None: ...


class ColourSelector(QDialog):
	colourChanged : ClassVar[Signal] = ...  # colourChanged(int, Colour)

	def __init__(self): ...
	def _setup_connections(self) -> None: ...
	def _setup_ui(self) -> None: ...
	def _slot_apply(self) -> None: ...
	def _slot_cancel(self) -> None: ...
	def _slot_filter(self) -> None: ...
	def _slot_tab_changed(self, index: int): ...
	def _slot_update_selection(self, index: int): ...


class _ColourScale(QWidget):
	def __init__(self, colours: list[Colour] = None, steps: int = 0, horizontal: bool = False): ...
	@classmethod
	def _segment_calculator(cls, colours: tuple[Colour], steps: int): ...
	def paintEvent(self, event: QPaintEvent) -> None: ...
	def update_scale(self, colours: list[Colour], steps: int): ...


class ColourScaleCreator(QDialog):
	colourScaleChanged : ClassVar[Signal] = ...  # colourScaleChanged(list)

	def __init__(self, colours: list[Colour] = None, horizontal: bool = False): ...
	def _setup_connections(self) -> None: ...
	def _setup_ui(self) -> None: ...
	def _slot_add_colour(self) -> None: ...
	def _slot_apply(self) -> None: ...
	def _slot_cancel(self) -> None: ...
	def _slot_update_scale(self) -> None: ...
	def _slot_update_total_steps(self) -> None: ...


class _TestApplication(QMainWindow):
	def __init__(self): ...
	def _setup_connections(self) -> None: ...
	def _setup_ui(self) -> None: ...
	@classmethod
	def _slot_cs_test(cls) -> None: ...
	@classmethod
	def _slot_csc_test(cls) -> None: ...
