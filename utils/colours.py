""" A module for adding the standard R colour palette to Qt applications. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
import json
import sys
from typing import Optional

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules/classes
# from Theme import set_widget_theme, WidgetTheme


TEXT_COLOUR_THRESHOLD = 100
ICON_FILE_PATH = ''
USE_THEME = False
COLOURS = None  # Getter defined later, after the class


def set_text_colour_threshold(new_value) -> None:
    """ Sets the threshold which represents the average intensity of colour
    channels above which the text should be black, while at or below it should
    be white.

    Parameters
    ----------
    new_value : int
        The new 8-bit threshold to set.
    """

    global TEXT_COLOUR_THRESHOLD
    TEXT_COLOUR_THRESHOLD = new_value


def set_icon_file_path(new_path='') -> None:
    """ Sets the path for the icon file to be used in the dialogs.

    Parameters
    ----------
    new_path : str, optional
        The new path to set. The default is an empty string, leading to the
        default icon.
    """

    global ICON_FILE_PATH
    ICON_FILE_PATH = new_path


def unlock_theme() -> None:
    """ Imports the theme module so the dialogs could be themed. """

    global USE_THEME
    USE_THEME = True
    from theme import set_widget_theme, WidgetTheme


class _ReadOnlyDescriptor:
    """ Read-only descriptor for use with protected storage attributes. """

    def __set_name__(self, owner, name):
        """ Sets the name of the storage attribute.
        Owner is the managed class, name is the managed attribute's name. """

        self._storage_name = f"_{name}"

    def __get__(self, instance, instance_type=None):
        """ Returns the value of the protected storage attribute. """

        return getattr(instance, self._storage_name)

    def __set__(self, instance, value):
        """ Raises an exception notifying the user about the attribute
        being read-only. """

        raise AttributeError(f"attribute '{self._storage_name[1:]}' of "
                             f"'{instance.__class__.__name__}' object "
                             f"is read-only")


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

    name = _ReadOnlyDescriptor()
    r = _ReadOnlyDescriptor()
    g = _ReadOnlyDescriptor()
    b = _ReadOnlyDescriptor()

    def __init__(self, name='white', r=255, g=255, b=255):
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

    @cached_property
    def as_rgb(self) -> str:
        """ Returns a string representation of the colour as [R, G, B]. """

        return f"[{self.r:03}, {self.g:03}, {self.b:03}]"

    @cached_property
    def as_hex(self) -> str:
        """ Returns the hexadecimal representation of the colour
        as '#RRGGBB'. """

        return f'#{self.r:02X}{self.g:02X}{self.b:02X}'

    def as_qt(self, negative=False) -> QColor:
        """ Returns a QColor object with the same RGB values
        (or its negative). """

        if negative:
            return QColor(255 - self.r, 255 - self.g, 255 - self.b)

        return QColor(self.r, self.g, self.b)

    def colour_box(self, width=20, height=20) -> QIcon:
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

        global TEXT_COLOUR_THRESHOLD
        if sum(self) / 3 > TEXT_COLOUR_THRESHOLD:
            return Qt.GlobalColor.black
        else:
            return Qt.GlobalColor.white

    @classmethod
    def _stub_repr(cls) -> str:
        """ Helper class method for stub file creation. """

        repr_ = f"class {cls.__name__}:\n"
        repr_ += "\tname: ''  # type: str\n"
        repr_ += "\tr: ''  # type: int\n"
        repr_ += "\tg: ''  # type: int\n"
        repr_ += "\tb: ''  # type: int\n"
        repr_ += "\tdef as_hex(self) -> str: ...\n"

        return repr_


class Colours:
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

            self._colours = {colour['name']: Colour(colour['name'],
                                                    colour['rgb'][0],
                                                    colour['rgb'][1],
                                                    colour['rgb'][2])
                             for colour in colours}

    def __getattr__(self, name):
        try:
            return getattr(self._colours, name)  # dict attributes
        except AttributeError:
            return self._colours[name]  # colour

    def __iter__(self):
        for colour in self._colours.values():
            yield colour

    def index(self, name) -> int:
        """ Returns the index of a given colour in the collection.

        Parameters
        ----------
        name : str
            The name of the colour to look up.
        """

        # Should be optimized if used more often
        return list(self._colours.keys()).index(name)

    def colour_at(self, idx) -> Colour:
        """ Returns the colour at the given numeric index.

        Parameters
        ----------
        idx : int
            The numeric index to look up.
        """

        # Should be optimized if used more often
        return self._colours[list(self._colours.keys())[idx]]

    @classmethod
    def _stub_repr(cls) -> str:
        """ Helper class method for stub file creation. """

        repr_ = f"class {cls.__name__}:\n"
        with open('colour_list.json', 'r') as f:
            colours = json.load(f)

        repr_ += '\n'.join([f"\t{colour['name']} = None  # type: Colour"
                            for colour in colours])

        return repr_


def get_colours() -> Colours:
    """ Creates a single instance of Colours, so it can be shared. """

    global COLOURS
    if COLOURS is None:
        COLOURS = Colours()

    return COLOURS


class ColourSelector(QDialog):
    """ A colour selector dialog. """

    colourChanged = Signal(int, Colour)

    def __init__(self, button_id, default_colour, widget_theme=None):
        """ Initializer for the class.

        Parameters
        ----------
        button_id : int
            An ID for the button to which the instance corresponds.

        default_colour : Colour
            The default colour the combobox icon should be set to.

        widget_theme : WidgetTheme, optional
            The theme used for the dialog. The default is None, for when
            theming is disabled.
        """

        super().__init__(parent=None)

        self.setWindowTitle("Colour selector")
        global ICON_FILE_PATH
        if ICON_FILE_PATH:
            self.setWindowIcon(QIcon(ICON_FILE_PATH))

        self.setFixedSize(400, 200)

        # Constants and variables
        self._button_id = button_id
        self._default_colour = default_colour
        self._colours = get_colours()
        self._widget_theme = widget_theme

        # GUI and layouts
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
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

        self._btnApply = QPushButton('Apply')
        self._btnApply.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogApplyButton))
        self._btnCancel = QPushButton('Cancel')
        self._btnCancel.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogCancelButton))

        # Layouts
        self._hloFilter = QHBoxLayout()
        self._hloFilter.addWidget(self._lblFilter)
        self._hloFilter.addWidget(self._ledFilter)
        self._hloFilter.addWidget(self._btnFilter)

        self._hloDialogButtons = QHBoxLayout()
        self._hloDialogButtons.addWidget(self._btnApply)
        self._hloDialogButtons.addWidget(self._btnCancel)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addLayout(self._hloFilter)
        self._vloMainLayout.addWidget(self._cmbColourList)
        self._vloMainLayout.addLayout(self._hloDialogButtons)

        self.setLayout(self._vloMainLayout)

        # Further initializations
        global USE_THEME
        if USE_THEME:
            # The drop-down menu must be forced not to use the system theme
            set_widget_theme(self._cmbColourList, self._widget_theme)
            set_widget_theme(self, self._widget_theme)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._ledFilter.returnPressed.connect(self._slot_filter)
        self._btnFilter.clicked.connect(self._slot_filter)
        self._btnApply.clicked.connect(self._slot_apply)
        self._btnCancel.clicked.connect(self._slot_cancel)

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

    def _slot_apply(self) -> None:
        """ Emits the ID of the set colour to the caller,
        then closes the window. """

        self.colourChanged.emit(self._button_id,
                                self._colours.colour_at(
                                    self._cmbColourList.currentIndex())
                                )
        self.close()

    def _slot_cancel(self) -> None:
        """ Closes the window without emitting a signal. """

        self.close()


@dataclass
class ColourBoxData:
    """ Data for an individual colour box in the drawer widget. """

    row: int = -1
    column: int = -1
    colour: Optional[Colour] = None

    def __post_init__(self):
        """ Add the default white colour. """

        if self.colour is None:
            self.colour = Colour()


class ColourBoxDrawer(QWidget):
    """ A selector widget showing all the colours as a grid of colour boxes.

    Methods
    -------
    get_selection()
        Returns the currently selected or the default colour.

    mousePressEvent(event)
        Handles colour selection graphically and by emitting a signal.

    keyPressEvent(event)
        Handles colour selection graphically and by emitting a signal.

    paintEvent(event)
        Prints the colour boxes and the selection rectangle.
    """

    colourSelected = Signal(int)

    def __init__(self, default_colour):
        """ Initializer for the class.

        Parameters
        ----------
        default_colour : Colour
            The default colour the combobox icon should be set to.
        """

        super().__init__(parent=None)

        self.setFixedSize(500, 450)

        self._default_colour = default_colour
        self._colours = get_colours()
        self._selection = ColourBoxData()
        self._boxes = []
        for idx, colour in enumerate(self._colours):
            self._boxes.append(ColourBoxData(idx // 25, idx % 25, colour))
            if colour == self._default_colour:
                self._selection.row = idx // 25
                self._selection.column = idx % 25
                self._selection.colour = colour

        self.update()

    def get_selection(self) -> Colour:
        """ Returns the currently selected or the default colour. """

        if self._selection.row < 0:
            return self._default_colour

        return self._selection.colour

    def mousePressEvent(self, event) -> None:
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

    def keyPressEvent(self, event) -> None:
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
            if index < 0:
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

    def paintEvent(self, event) -> None:
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


class ExtendedColourSelector(QDialog):
    """ An extended colour selector dialog. """

    colourChanged = Signal(int, Colour)

    def __init__(self, button_id, default_colour, widget_theme=None):
        """ Initializer for the class.

        Parameters
        ----------
        button_id : int
            An ID for the button to which the instance corresponds.

        default_colour : Colour
            The default colour the drawer should be set to.

        widget_theme : WidgetTheme, optional
            The theme used for the dialog. The default is None, for when
            theming is disabled.
        """

        super().__init__(parent=None)

        self.setWindowTitle("Extended colour selector")
        global ICON_FILE_PATH
        if ICON_FILE_PATH:
            self.setWindowIcon(QIcon(ICON_FILE_PATH))

        self.setFixedSize(525, 575)

        # Constants and variables
        self._button_id = button_id
        self._default_colour = default_colour
        self._widget_theme = widget_theme

        # GUI and layouts
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._lblCurrentColour = QLabel(
            text=f"Selection: {self._default_colour.name}", parent=None)
        self._lblCurrentColourRGB = QLabel(
            text=f"RGB: {self._default_colour.as_rgb}", parent=None)
        self._lblCurrentColourHex = QLabel(
            text=f"Hex: {self._default_colour.as_hex}", parent=None)

        self._colourBoxDrawer = ColourBoxDrawer(self._default_colour)

        self._btnApply = QPushButton('Apply')
        self._btnApply.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogApplyButton))
        self._btnCancel = QPushButton('Cancel')
        self._btnCancel.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogCancelButton))

        # Layouts
        self._vloSelectionInformation = QVBoxLayout()
        self._vloSelectionInformation.addWidget(self._lblCurrentColour)
        self._vloSelectionInformation.addWidget(self._lblCurrentColourRGB)
        self._vloSelectionInformation.addWidget(self._lblCurrentColourHex)

        self._hloDialogButtons = QHBoxLayout()
        self._hloDialogButtons.addWidget(self._btnApply)
        self._hloDialogButtons.addWidget(self._btnCancel)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addLayout(self._vloSelectionInformation)
        self._vloMainLayout.addWidget(self._colourBoxDrawer)
        self._vloMainLayout.addLayout(self._hloDialogButtons)

        self.setLayout(self._vloMainLayout)

        # Further initializations
        self._colourBoxDrawer.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._colourBoxDrawer.setFocus()
        global USE_THEME
        if USE_THEME:
            set_widget_theme(self, self._widget_theme)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._colourBoxDrawer.colourSelected.connect(
            self._slot_update_selection)
        self._btnApply.clicked.connect(self._slot_apply)
        self._btnCancel.clicked.connect(self._slot_cancel)

    def _slot_update_selection(self, index):
        """ Updates the data of the currently selected colour. """

        self._lblCurrentColour.setText(
            f"Selection: {self._colourBoxDrawer.get_selection().name}")
        self._lblCurrentColourRGB.setText(
            f"RGB: {self._colourBoxDrawer.get_selection().as_rgb}")
        self._lblCurrentColourHex.setText(
            f"Hex: {self._colourBoxDrawer.get_selection().as_hex}")

    def _slot_apply(self) -> None:
        """ Emits the ID of the set colour to the caller,
        then closes the window. """

        self.colourChanged.emit(self._button_id,
                                self._colourBoxDrawer.get_selection())
        self.close()

    def _slot_cancel(self) -> None:
        """ Closes the window without emitting a signal. """

        self.close()


class TestApplication(QMainWindow):
    """ The entry point for testing.

    Methods
    -------
    closeEvent(event)
        Overrides the default close event and shows a dialog that asks
        the user if they really want to quit.
    """

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
        self._btnExtendedColourSelector = QPushButton("Open an extended colour "
                                                      "selector dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnColourSelector)
        self._vloMainLayout.addWidget(self._btnExtendedColourSelector)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnColourSelector.clicked.connect(self._slot_cs_test)
        self._btnExtendedColourSelector.clicked.connect(self._slot_ecs_test)

    @staticmethod
    def _slot_cs_test() -> None:
        """ Tests the colour selector dialog. """

        def catch_signal(button_id, colour) -> None:
            print(f"Signal caught: ({button_id}, {colour})")

        cs = ColourSelector(0, Colour())
        cs.colourChanged.connect(catch_signal)
        cs.exec()

    @staticmethod
    def _slot_ecs_test() -> None:
        """ Tests the colour selector dialog. """

        def catch_signal(button_id, colour) -> None:
            print(f"Signal caught: ({button_id}, {colour})")

        ecs = ExtendedColourSelector(0, Colour())
        ecs.colourChanged.connect(catch_signal)
        ecs.exec()


def _create_stub_file() -> None:
    """ Allows auto-completion of dynamic attributes; helper function. """

    with open('colours.pyi', 'w') as f:
        f.write(Colour._stub_repr())
        f.write('\n')
        f.write(Colours._stub_repr())


# INITIALIZE THE MODULE
get_colours()


if __name__ == '__main__':
    # _create_stub_file()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = TestApplication()
    mainWindow.show()
    app.exec()
