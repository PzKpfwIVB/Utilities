""" A module for adding the standard R colour palette to Qt applications. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.3.4'

# Built-in modules
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from itertools import pairwise
import json
import os
import sys
from typing import Optional

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules/classes
from utils._general import (BijectiveDict, ReadOnlyDescriptor, SignalBlocker,
                            Singleton, stub_repr)


_TEXT_COLOUR_THRESHOLD = 100
_ICON_FILE_PATH = ''
_EXTENDED_DEFAULT = False
_USE_THEME = False
Colours: _Colours | None = None


def text_colour_threshold() -> int:
    """ Returns the threshold which represents the average intensity of colour
        channels above which the text should be black, while at or below it
        should be white. """

    return _TEXT_COLOUR_THRESHOLD


def set_text_colour_threshold(new_value: int) -> None:
    """ Sets the threshold which represents the average intensity of colour
    channels above which the text should be black, while at or below it should
    be white.

    Parameters
    ----------
    new_value : int
        The new 8-bit threshold to set.
    """

    global _TEXT_COLOUR_THRESHOLD
    _TEXT_COLOUR_THRESHOLD = new_value


def icon_file_path() -> str:
    """ Returns the path for the icon file to be used in the dialogs. """

    return _ICON_FILE_PATH


def set_icon_file_path(new_path: str = '') -> None:
    """ Sets the path for the icon file to be used in the dialogs.

    Parameters
    ----------
    new_path : str, optional
        The new path to set. The default is an empty string, leading to the
        default icon.
    """

    global _ICON_FILE_PATH
    _ICON_FILE_PATH = new_path


def extended_default() -> bool:
    """ Returns the flag controlling the default tab of the colour selector. """

    return _EXTENDED_DEFAULT


def set_extended_default(new_default: bool) -> None:
    """ Returns the flag controlling the default tab of the colour selector.

    Parameters
    ----------
    new_default : bool
        The new flag to set.
    """

    global _EXTENDED_DEFAULT
    _EXTENDED_DEFAULT = new_default


def unlock_theme() -> None:
    """ Imports the theme module so the dialogs could be themed. """

    global _USE_THEME
    _USE_THEME = True
    from utils.theme import set_widget_theme, WidgetTheme


class Colour:
    """ A class to represent an RGB colour.

    Methods
    -------
    as_rgb()
        Returns a string representation of the colour as [R, G, B].

    as_hex()
        Returns the hexadecimal representation of the colour as '#RRGGBB'.

    as_qt()
        Returns a QColor object with the same RGB values (or its negative).

    colour_box(width, height)
        Returns a colour box as a QIcon with the requested size.

    text_colour()
        Returns the (black/white) QColor that's appropriate to
        write with on the background with the given colour.
    """

    name = ReadOnlyDescriptor()
    r = ReadOnlyDescriptor()
    g = ReadOnlyDescriptor()
    b = ReadOnlyDescriptor()

    def __init__(self, name: str = 'white', r: int = 255, g: int = 255,
                 b: int = 255):
        """ Initializer for the class. By default, it creates a white object.

        Parameters
        ----------
        name : str, optional
            The name of the colour. The default value is 'white'.

        r : int, optional
            The 8-bit red value of the colour. The default value is 255.

        g : int, optional
            The 8-bit green value of the colour. The default value is 255.

        b : int, optional
            The 8-bit blue value of the colour. The default value is 255.
        """

        self._name = name
        self._r = r
        self._g = g
        self._b = b

    def __repr__(self):
        return f"Colour('{self.name}', {self.r}, {self.g}, {self.b})"

    def __str__(self):
        return f'Colour({self.name} :: [{self.r}, {self.g}, {self.b}])'

    def __eq__(self, other):
        if isinstance(other, Colour):
            other_colour = (other.r, other.g, other.b)
        elif isinstance(other, Iterable):
            other_colour = other[:3]
        elif isinstance(other, QColor):
            other_colour = (other.red(), other.green(), other.blue())
        else:
            return id(self) == id(other)

        return all(ch_a == ch_b for (ch_a, ch_b)
                   in zip((self.r, self.g, self.b), other_colour))

    def __iter__(self):
        for ch in (self.r, self.g, self.b):
            yield ch

    def __hash__(self):
        return hash((self.name, self.r, self.g, self.b))

    @cached_property
    def as_rgb(self) -> str:
        """ Returns a string representation of the colour as [R, G, B]. """

        return f"[{self.r:03}, {self.g:03}, {self.b:03}]"

    @cached_property
    def as_hex(self) -> str:
        """ Returns the hexadecimal representation of the colour
        as '#RRGGBB'. """

        return f'#{self.r:02X}{self.g:02X}{self.b:02X}'

    def as_qt(self, negative: bool = False) -> QColor:
        """ Returns a QColor object with the same RGB values
        (or its negative). """

        if negative:
            return QColor(255 - self.r, 255 - self.g, 255 - self.b)

        return QColor(self.r, self.g, self.b)

    def colour_box(self, width: int = 20, height: int = 20) -> QIcon:
        """ Returns a colour box as a QIcon with the requested size.

        Parameters
        ----------
        width : int, optional
            The requested width of the colour box. The default is 20 pixels.

        height : int, optional
            The requested height of the colour box. The default is 20 pixels.
        """

        pixmap = QPixmap(width, height)
        pixmap.fill(self.as_qt())

        return QIcon(pixmap)

    def text_colour(self) -> Qt.GlobalColor:
        """ Returns the (black/white) QColor that's appropriate to write with
        on the background with the given colour. """

        if sum(self) / 3 > _TEXT_COLOUR_THRESHOLD:
            return Qt.GlobalColor.black
        else:
            return Qt.GlobalColor.white


class _Colours(metaclass=Singleton):
    """ A collection of colours of the standard R colour palette.

    Methods
    -------
    index(name)
        Returns the index of a given colour in the collection.

    colour_at(idx)
        Returns the colour at the given numeric index.
    """

    def __init__(self):
        """ Initializer for the class. """

        with open('colour_list.json', 'r') as f:
            colours = json.load(f)

            self._colours_int = BijectiveDict(int)
            self._colours_str = BijectiveDict(str)
            for idx, colour_data in enumerate(colours):
                colour = Colour(colour_data['name'], *colour_data['rgb'])
                self._colours_int[idx] = colour
                self._colours_str[colour.name] = colour

    def __getattr__(self, name):
        try:
            return getattr(self._colours_str, name)  # dict attributes
        except AttributeError:
            return self._colours_str[name]  # Colour object

    def __iter__(self):
        for colour in self._colours_int.values():
            yield colour

    def __getitem__(self, index):
        if isinstance(index, int | Colour):
            return self._colours_int[index]
        else:  # str
            colour = self._colours_str[index]  # Might need to be moved to a f()
            return colour, self._colours_int[colour]  # (Colour, int)

    def index(self, name: str) -> int:
        """ Returns the index of a given colour in the collection.

        Parameters
        ----------
        name : str
            The name of the colour to look up.
        """

        return self._colours_int[self._colours_str[name]]  # str->Colour->int

    def colour_at(self, idx: int) -> Colour:
        """ Returns the colour at the given numeric index.

        Parameters
        ----------
        idx : int
            The numeric index to look up.
        """

        return self._colours_int[idx]

    def from_qt(self, qc: QColor) -> Colour:
        """ Returns an existing colour or an unnamed custom one.

        Parameters
        ----------
        qc : QColor
            The Qt colour based on which the search is to be conducted.
        """

        channels = [('r', 'red'), ('g', 'green'), ('b', 'blue')]
        for colour in self._colours_int.values():
            if all(getattr(colour, ch1) == getattr(qc, ch2)()
                   for ch1, ch2 in channels):
                return colour

        return Colour('unnamed', *[getattr(qc, ch)() for _, ch in channels])


@dataclass
class _ColourBoxData:
    """ Data for an individual colour box in the drawer widget. """

    row: int = -1
    column: int = -1
    colour: Optional[Colour] = None

    def __post_init__(self):
        """ Add the default white colour. """

        if self.colour is None:
            self.colour = Colour()


class _ColourBoxDrawer(QWidget):
    """ A selector widget showing all the colours as a grid of colour boxes.

    Methods
    -------
    selection()
        Returns the currently selected or the default colour.

    selection(new_selection)
        Sets a new selection (made by an external sender).

    mousePressEvent(event)
        Handles colour selection graphically and by emitting a signal.

    keyPressEvent(event)
        Handles colour selection graphically and by emitting a signal.

    paintEvent(event)
        Prints the colour boxes and the selection rectangle.
    """

    colourSelected = Signal(int)

    def __init__(self, default_colour: Colour):
        """ Initializer for the class.

        Parameters
        ----------
        default_colour : Colour
            The default colour the combobox icon should be set to.
        """

        super().__init__(parent=None)

        self.setFixedSize(500, 450)

        self._default_colour = default_colour
        self._colours = Colours
        self._selection = _ColourBoxData()
        self._boxes = []
        for idx, colour in enumerate(self._colours):
            self._boxes.append(_ColourBoxData(idx // 25, idx % 25, colour))
            if colour == self._default_colour:
                self._selection.row = idx // 25
                self._selection.column = idx % 25
                self._selection.colour = colour

        self.update()

    @property
    def selection(self) -> Colour:
        """ Returns the currently selected or the default colour. """

        if self._selection.row < 0:
            return self._default_colour

        return self._selection.colour

    @selection.setter
    def selection(self, new_selection: _ColourBoxData) -> None:
        """ Sets a new selection (made by an external sender).

        Parameters
        ----------
        new_selection : _ColourBoxData
            The new selection to set.
        """

        self._selection = new_selection

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """ Handles colour selection graphically and by emitting a signal.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event that triggered the method.
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self._selection.row = int(event.position().y()) // 20
            self._selection.column = int(event.position().x()) // 20
            index = self._selection.row * 25 + self._selection.column
            try:
                self._selection.colour = self._boxes[index].colour
            except IndexError:
                pass
            else:
                self.update()
                self.colourSelected.emit(index)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """ Handles colour selection graphically and by emitting a signal.

        Parameters
        ----------
        event : QKeyEvent
            The mouse event that triggered the method.
        """

        index_modifiers = {
            Qt.Key.Key_Up: {'row': -1, 'column': 0},
            Qt.Key.Key_Down: {'row': 1, 'column': 0},
            Qt.Key.Key_Left: {'row': 0, 'column': -1},
            Qt.Key.Key_Right: {'row': 0, 'column': 1}
        }

        if (key := event.key()) in index_modifiers.keys():
            row_history = self._selection.row
            col_history = self._selection.column

            self._selection.row += index_modifiers[key]['row']
            self._selection.column += index_modifiers[key]['column']
            index = self._selection.row * 25 + self._selection.column

            if not all(0 <= x < 25 for x in [self._selection.row,
                                             self._selection.column]):
                self._selection.row = row_history
                self._selection.column = col_history
                return

            try:
                self._selection.colour = self._boxes[index].colour
            except IndexError:
                self._selection.row = row_history
                self._selection.column = col_history
            else:
                self.update()
                self.colourSelected.emit(index)

    def paintEvent(self, event: QPaintEvent) -> None:
        """ Prints the colour boxes and the selection rectangle.

        Parameters
        ----------
        event : QPaintEvent
            The paint event that triggered the method.
        """

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for box in self._boxes:
            painter.fillRect(box.column * 20, box.row * 20,
                             20, 20, box.colour.as_qt())

        if self._selection.row != -1:
            painter.setPen(self._selection.colour.text_colour())
            painter.drawRect(self._selection.column * 20,
                             self._selection.row * 20,
                             20, 20)


class ColourSelector(QDialog):
    """ A colour selector dialog. """

    colourChanged = Signal(int, Colour)

    def __init__(self, button_id=0, default_colour=Colour(), widget_theme=None):
        """ Initializer for the class.

        Parameters
        ----------
        button_id : int, optional
            An ID for the button to which the instance corresponds. The default
            is 0.

        default_colour : Colour, optional
            The default colour the combobox icon should be set to. The default
            is white.

        widget_theme : WidgetTheme, optional
            The theme used for the dialog. The default is None, for when
            theming is disabled.
        """

        super().__init__(parent=None)

        self.setWindowTitle("Colour selector")
        if _ICON_FILE_PATH:
            self.setWindowIcon(QIcon(_ICON_FILE_PATH))

        self.setFixedSize(540, 605)

        # Constants and variables
        self._button_id = button_id
        self._default_colour = default_colour
        self._colours = Colours
        self._extended = _EXTENDED_DEFAULT
        self._widget_theme = widget_theme

        # GUI and layouts
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # ===== GUI objects =====
        # Simple selector
        self._wdgSimpleSelector = QWidget(self)

        self._lblFilter = QLabel(text="List filter:", parent=None)
        self._ledFilter = QLineEdit('', parent=None)
        self._btnFilter = QPushButton()
        self._btnFilter.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self._btnFilter.setGeometry(0, 0, 50, 22)

        self._cmbColourList = QComboBox(parent=None)
        for colour in self._colours:
            self._cmbColourList.addItem(colour.colour_box(), colour.name)

        self._cmbColourList.setCurrentIndex(
            self._colours.index(self._default_colour.name))

        self._cmbColourList.setStyleSheet("combobox-popup: 0")
        self._cmbColourList.setObjectName('combobox')

        # Extended selector
        self._wdgExtendedSelector = QWidget(self)

        self._lblCurrentColour = QLabel(
            text=f"Selection: {self._default_colour.name}", parent=None)
        self._lblCurrentColourRGB = QLabel(
            text=f"RGB: {self._default_colour.as_rgb}", parent=None)
        self._lblCurrentColourHex = QLabel(
            text=f"Hex: {self._default_colour.as_hex}", parent=None)

        self._colourBoxDrawer = _ColourBoxDrawer(self._default_colour)
        self._colourBoxDrawer.setObjectName('drawer')

        # Main objects
        self._tabSelectors = QTabWidget()

        self._btnApply = QPushButton('Apply')
        self._btnApply.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogApplyButton))
        self._btnCancel = QPushButton('Cancel')
        self._btnCancel.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogCancelButton))

        # ===== Layouts =====
        # Simple selector
        self._hloFilter = QHBoxLayout()
        self._hloFilter.addWidget(self._lblFilter)
        self._hloFilter.addWidget(self._ledFilter)
        self._hloFilter.addWidget(self._btnFilter)

        self._vloSimpleSelector = QVBoxLayout()
        self._vloSimpleSelector.addLayout(self._hloFilter)
        self._vloSimpleSelector.addWidget(self._cmbColourList)
        self._vloSimpleSelector.addStretch(0)

        self._wdgSimpleSelector.setLayout(self._vloSimpleSelector)

        # Extended selector
        self._vloExtendedSelector = QVBoxLayout()
        self._vloExtendedSelector.addWidget(self._lblCurrentColour)
        self._vloExtendedSelector.addWidget(self._lblCurrentColourRGB)
        self._vloExtendedSelector.addWidget(self._lblCurrentColourHex)
        self._vloExtendedSelector.addWidget(self._colourBoxDrawer)

        self._wdgExtendedSelector.setLayout(self._vloExtendedSelector)

        # Main layout
        self._tabSelectors.addTab(self._wdgSimpleSelector, 'Simple')
        self._tabSelectors.addTab(self._wdgExtendedSelector, 'Extended')

        self._hloDialogButtons = QHBoxLayout()
        self._hloDialogButtons.addWidget(self._btnApply)
        self._hloDialogButtons.addWidget(self._btnCancel)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._tabSelectors)
        self._vloMainLayout.addLayout(self._hloDialogButtons)

        self.setLayout(self._vloMainLayout)

        # ===== Further initializations =====
        if self._extended:
            self._tabSelectors.setCurrentIndex(1)

        if _USE_THEME:
            # The drop-down menu must be forced not to use the system theme
            set_widget_theme(self._cmbColourList, self._widget_theme)
            set_widget_theme(self, self._widget_theme)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._ledFilter.returnPressed.connect(self._slot_filter)
        self._btnFilter.clicked.connect(self._slot_filter)
        self._cmbColourList.currentIndexChanged.connect(
            self._slot_update_selection)

        self._colourBoxDrawer.colourSelected.connect(
            self._slot_update_selection)

        self._tabSelectors.currentChanged.connect(self._slot_tab_changed)

        self._btnApply.clicked.connect(self._slot_apply)
        self._btnCancel.clicked.connect(self._slot_cancel)

    def _slot_tab_changed(self, index: int):
        """ Handles tab changes.

        Parameters
        ----------
        index : int
            The index of the new tab.
        """

        if index == 1:  # Extended selector
            self._colourBoxDrawer.setFocus()

    def _slot_filter(self) -> None:
        """ Filters the colour list based on the text in line edit. """

        new_index = -1
        for idx, colour in enumerate(self._colours):
            condition = self._ledFilter.text().lower() in colour.name
            self._cmbColourList.view().setRowHidden(idx, not condition)
            if condition and new_index == -1:
                new_index = idx

        self._cmbColourList.setCurrentIndex(new_index)
        self._cmbColourList.view().setFixedHeight(200)

    def _slot_update_selection(self, index: int):
        """ Updates the data of the currently selected colour.

        Parameters
        ----------
        index : int
            The index of the new colour from a combobox or a selector dialog.
        """

        if (sender := self.sender().objectName()) == 'combobox':
            with SignalBlocker(self._colourBoxDrawer) as obj:
                obj.selection = _ColourBoxData(
                    row=index // 25,
                    column=index % 25,
                    colour=self._colours.colour_at(index)
                )
        elif sender == 'drawer':  # elif for possible future expansion
            with SignalBlocker(self._cmbColourList) as obj:
                obj.setCurrentIndex(index)

        self._lblCurrentColour.setText(
            f"Selection: {self._colourBoxDrawer.selection.name}")
        self._lblCurrentColourRGB.setText(
            f"RGB: {self._colourBoxDrawer.selection.as_rgb}")
        self._lblCurrentColourHex.setText(
            f"Hex: {self._colourBoxDrawer.selection.as_hex}")

    def _slot_apply(self) -> None:
        """ Emits the ID of the set colour to the caller,
        then closes the window. """

        # Selection is synchronized among selectors
        self.colourChanged.emit(self._button_id,
                                self._colourBoxDrawer.selection)
        self.close()

    def _slot_cancel(self) -> None:
        """ Closes the window without emitting a signal. """

        self.close()


class _ColourScale(QWidget):
    """ A widget that draws a 500px vertical/horizontal colour scale.

    Methods
    -------
    update_scale(colours, steps)
        Sets new controls to update the scale.

    paintEvent(event)
        Draws the requested scale.
    """

    def __init__(self, colours: list[Colour] = None, steps: int = 0,
                 horizontal: bool = False):
        """ Initializer for the class.

        Parameters
        ----------
        colours : list[Colour], optional
            The list of colours on which the scale is based. The default is
            None, resulting in a blank colour scale.

        steps : int, optional
            The number of steps of colours between two set colours.
            The default is 0, corresponding to an empty colour list.

        horizontal : bool, optional
            A flag marking whether the scale is horizontal. The default is
            False (vertical scale).
        """

        super().__init__(parent=None)

        self._colours: list[Colour] = colours
        self.scale_colours: list[QColor] | None = None  # Calculated list
        self._steps = steps
        self._horizontal = horizontal
        if self._horizontal:
            self.setFixedSize(500, 20)
            self._bottom_right = QPoint(500, 20)
        else:
            self.setFixedSize(20, 500)
            self._bottom_right = QPoint(20, 500)

    def update_scale(self, colours: list[Colour], steps: int):
        """ Sets new controls to update the scale.

        Parameters
        ----------
        colours : list[Colour]
            The list of colours on which the scale is based.

        steps : int
            The number of steps of colours between two set colours.
        """

        self._colours = colours
        self._steps = steps
        self.update()

    @classmethod
    def _segment_calculator(cls, colours: tuple[Colour], steps: int):
        """ Calculates the colours of a segment of the scale, which is between
        two set colours.

        Parameters
        ----------
        colours : tuple[Colour]
            A pair of colours at the edges of the segment.

        steps : int
            The number of steps of colours between two set colours.
        """

        def _to_8_bit(value) -> int:
            """ Coerces a value to be between 0 and 255 and returns
            it as an integer. """

            return int(min(255, max(0, value)))

        start: Colour = colours[0]
        end: Colour = colours[1]

        step_sizes = {'r': 0, 'g': 0, 'b': 0}
        channel_wise = {'r': None, 'g': None, 'b': None}
        for ch in step_sizes.keys():
            step_sizes[ch] = (abs(getattr(end, ch) - getattr(start, ch)) /
                              (steps - 1))
            sign = 1 if getattr(end, ch) >= getattr(start, ch) else -1
            if step_sizes[ch] != 0:
                internal = [_to_8_bit(getattr(start, ch) +
                                      i * sign * step_sizes[ch])
                            for i in range(steps)]
            else:
                internal = [getattr(start, ch) for _ in range(steps)]

            channel_wise[ch] = internal + [getattr(end, ch)]

        return [QColor(r, g, b) for r, g, b in zip(*channel_wise.values())]

    def paintEvent(self, event: QPaintEvent) -> None:
        """ Draws the requested scale.

        Parameters
        ----------
        event : QPaintEvent
            The paint event that triggered the method.
        """

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._colours is None or len(self._colours) == 0:
            rect = QRect(QPoint(0, 0), self._bottom_right)
            painter.fillRect(rect, Qt.GlobalColor.white)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawRect(rect)
            return

        self.scale_colours = [self._colours[0].as_qt()]
        for pair in pairwise(self._colours):
            self.scale_colours.extend(
                self._segment_calculator(pair, self._steps))

        last_coordinate = 0
        step_size = 500 / len(self.scale_colours)
        for colour in self.scale_colours:
            if self._horizontal:
                start = QPoint(last_coordinate, 0)
                end = QPoint(int(last_coordinate + step_size), 20)
            else:
                start = QPoint(0, last_coordinate)
                end = QPoint(20, int(last_coordinate + step_size))

            painter.fillRect(QRect(start, end), colour)
            last_coordinate = last_coordinate + step_size


class ColourScaleCreator(QDialog):
    """ A dialog for creating a custom colour scale. """

    colourScaleChanged = Signal(list)

    def __init__(self, colours: list[Colour] = None, horizontal: bool = False):
        """ Initializer for the class.

        Parameters
        ----------
        colours : list[Colour], optional
            The list of colours to set for the scale. The default is None,
            resulting in a default white scale.

        horizontal : bool, optional
            A flag marking whether a vertical (default) or horizontal scale
            should be used in the dialog.
        """

        super().__init__(parent=None)

        self.setWindowTitle("Colour scale creator")
        self.setFixedSize(525, 560)

        self._scale_colours = colours
        self._colours = Colours
        self._horizontal = horizontal
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._h_scale = _ColourScale(self._scale_colours, horizontal=True)
        self._v_scale = _ColourScale(self._scale_colours)
        if self._horizontal:
            self._v_scale.setVisible(False)
        else:
            self._h_scale.setVisible(False)

        self._lwColours = QListWidget()
        self._lwColours.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove)

        self._btnAddColour = QPushButton("Add colour")
        self._lblSteps = QLabel(text='Steps', parent=None)
        self._spbSteps = QSpinBox()
        self._spbSteps.setMaximum(1000)  # Arbitrarily chosen limit
        self._spbSteps.setToolTip("Numer of steps among consecutively "
                                  "set colours")
        self._lblTotalSteps = QLabel("Total steps:\n0")
        self._btnUpdate = QPushButton("Update scale")

        self._btnApply = QPushButton('Apply')
        self._btnApply.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogApplyButton))
        self._btnCancel = QPushButton('Cancel')
        self._btnCancel.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogCancelButton))

        # Layouts
        self._vloScaleControls = QVBoxLayout()
        self._vloScaleControls.addWidget(self._btnAddColour)
        self._vloScaleControls.addWidget(self._lblSteps)
        self._vloScaleControls.addWidget(self._spbSteps)
        self._vloScaleControls.addWidget(self._lblTotalSteps)
        self._vloScaleControls.addWidget(self._btnUpdate)
        self._vloScaleControls.addStretch(0)

        self._hloScaleSection = QHBoxLayout()
        self._hloScaleSection.addWidget(self._v_scale)
        self._hloScaleSection.addWidget(self._lwColours)
        self._hloScaleSection.addLayout(self._vloScaleControls)

        self._hloDialogButtons = QHBoxLayout()
        self._hloDialogButtons.addWidget(self._btnApply)
        self._hloDialogButtons.addWidget(self._btnCancel)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._h_scale)
        self._vloMainLayout.addLayout(self._hloScaleSection)
        self._vloMainLayout.addLayout(self._hloDialogButtons)

        self.setLayout(self._vloMainLayout)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnAddColour.clicked.connect(self._slot_add_colour)
        self._spbSteps.valueChanged.connect(self._slot_update_total_steps)
        self._btnUpdate.clicked.connect(self._slot_update_scale)

        self._btnApply.clicked.connect(self._slot_apply)
        self._btnCancel.clicked.connect(self._slot_cancel)

    def _slot_update_total_steps(self) -> None:
        """ Updates the label showing the total number of colour steps. """

        cc = self._lwColours.count()
        if cc <= 1:
            steps = 0
        else:
            steps = cc + self._spbSteps.value() * (cc - 1)

        self._lblTotalSteps.setText(f"Total steps:\n{steps}")

    def _slot_add_colour(self) -> None:
        """ Adds a colour to the list widget and updates the
        label accordingly. """

        def catch_signal(button_id, colour) -> None:
            """ Catches the signal carrying the newly set colour.

            Parameters
            ----------
            button_id : int
                The caller button's ID, unused here.

            colour : Colour
                The colour to add to the list.
            """

            lwi = QListWidgetItem(colour.colour_box(), colour.name)
            self._lwColours.addItem(lwi)
            self._slot_update_total_steps()

        cs = ColourSelector()
        cs.colourChanged.connect(catch_signal)
        cs.exec()

    def _slot_update_scale(self) -> None:
        """ Sends the set colours to the scale widget for it to get updated. """

        self._scale_colours = [self._colours[
                                   self._lwColours.item(idx).text()][0]
                               for idx in range(self._lwColours.count())]
        steps = self._spbSteps.value()

        if self._horizontal:
            self._h_scale.update_scale(self._scale_colours, steps)
        else:
            self._v_scale.update_scale(self._scale_colours, steps)

    def _slot_apply(self) -> None:
        """ Emits the calculated scale colours, then closes the window. """

        if self._horizontal:
            self.colourScaleChanged.emit(self._h_scale.scale_colours)
        else:
            self.colourScaleChanged.emit(self._v_scale.scale_colours)

        self.close()

    def _slot_cancel(self) -> None:
        """ Closes the window without emitting a signal. """

        self.close()


class _TestApplication(QMainWindow):
    """ The entry point for testing. """

    def __init__(self):
        """ Constructor method for the Application class (the main class). """

        super().__init__()

        self.setWindowTitle("Test application")

        # GUI and layouts
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._btnColourSelector = QPushButton("Open a colour selector dialog")
        self._btnColourScaleCreator = QPushButton("Open a colour scale creator "
                                                  "dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnColourSelector)
        self._vloMainLayout.addWidget(self._btnColourScaleCreator)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnColourSelector.clicked.connect(self._slot_cs_test)
        self._btnColourScaleCreator.clicked.connect(self._slot_csc_test)

    @classmethod
    def _slot_cs_test(cls) -> None:
        """ Tests the colour selector dialog. """

        def catch_signal(button_id, colour) -> None:
            """ Catches the signal carrying the newly set colour.

            Parameters
            ----------
            button_id : int
                The caller button's ID, here used only for reporting it back.

            colour : Colour
                The set colour, here used only for reporting it back.
            """

            print(f"Signal caught: ({button_id}, {colour})")

        cs = ColourSelector(0, Colour())
        cs.colourChanged.connect(catch_signal)
        cs.exec()

    @classmethod
    def _slot_csc_test(cls) -> None:
        """ Tests the colour scale creator dialog. """

        csc = ColourScaleCreator()
        csc.exec()


def _init_module():
    """ Initializes the module. """

    if not os.path.exists('colours.pyi'):
        imports = "from dataclasses import dataclass\n" \
                  "from functools import cached_property\n" \
                  "from typing import ClassVar, Optional\n" \
                  "from PySide6.QtCore import Signal, Qt\n" \
                  "from PySide6.QtGui import QColor, QIcon, QKeyEvent, " \
                  "QMouseEvent, QPaintEvent\n" \
                  "from PySide6.QtWidgets import QDialog, QMainWindow, " \
                  "QWidget\n" \
                  "from utils._general import ReadOnlyDescriptor, Singleton" \
                  "\n\n\n"

        reprs = []
        functions = [text_colour_threshold, set_text_colour_threshold,
                     icon_file_path, set_icon_file_path, extended_default,
                     set_extended_default, unlock_theme]
        for func in functions:
            reprs.append(stub_repr(func))

        reprs.append('\n\n')

        class_reprs = []
        classes = {Colour: None,
                   _Colours: None,
                   _ColourBoxData: None,
                   _ColourBoxDrawer: ['colourSelected(int)'],
                   ColourSelector: ['colourChanged(int, Colour)'],
                   _ColourScale: None,
                   ColourScaleCreator: ['colourScaleChanged(list)'],
                   _TestApplication: None}
        for cls, sigs in classes.items():
            if cls == _Colours:
                with open('colour_list.json', 'r') as f:
                    colours = json.load(f)

                extra_cvs = '\n'.join([f"\t{colour['name']}: Colour = None"
                                       for colour in colours])
            else:
                extra_cvs = None

            class_reprs.append(stub_repr(cls, signals=sigs,
                                         extra_cvs=extra_cvs))

        reprs.append('\n\n'.join(class_reprs))

        with open('colours.pyi', 'w') as f:
            f.write(imports)
            f.write("Colours: _Colours = None\n\n\n")
            f.write(''.join(reprs))

    global Colours
    Colours = _Colours()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
