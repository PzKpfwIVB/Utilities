""" A module for simplifying the use of creators from other modules by a simple
universal application. """

__author__ = "Mihaly Konda"
__version__ = '1.0.1'

# Built-in modules
import sys

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules/classes
from utils_qt_mk.config import use_theme
_USE_THEME = use_theme()

from utils_qt_mk.colours import ColourScaleCreator
from utils_qt_mk.custom_file_dialog import _FileDialogDataEditor  # type: ignore
from utils_qt_mk.general import qt_connect
from utils_qt_mk.message import _MessageBoxTypeCreator  # type: ignore
if _USE_THEME:
    from utils_qt_mk.theme import WidgetTheme
    from utils_qt_mk.theme_creator import ThemeCreator


class _CreatorCentre(QMainWindow):
    """ A unified application for all available creators. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

        self.setWindowTitle("Creator Centre")

        # GUI and layouts
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._btnColourScaleCreator = QPushButton("Open a colour scale creator "
                                                  "dialog")
        self._btnFileDialogCreator = QPushButton("Open a file dialog creator")
        self._btnMBTCreator = QPushButton("Open a MessageBoxType creator")
        self._btnThemeCreator = QPushButton("Open a theme creator")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnColourScaleCreator)
        self._vloMainLayout.addWidget(self._btnFileDialogCreator)
        self._vloMainLayout.addWidget(self._btnMBTCreator)
        self._vloMainLayout.addWidget(self._btnThemeCreator)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._btnColourScaleCreator.clicked,
                   self._slot_colour_scale_creator)
        qt_connect(self._btnFileDialogCreator.clicked,
                   self._slot_file_dialog_creator)
        qt_connect(self._btnMBTCreator.clicked, self._slot_mbt_creator)
        qt_connect(self._btnThemeCreator.clicked, self._slot_theme_creator)

    def _slot_colour_scale_creator(self) -> None:
        """ Shows the colour scale creator. """

        def catch_signal(colour_list: list) -> None:
            """ Catches the signal carrying the newly set colour.

            :param colour_list: The list of colours of the created scale.
            """

            print(f"Signal caught: ({colour_list})")

        theme = None if not _USE_THEME else WidgetTheme.dark
        self._csc = ColourScaleCreator(widget_theme=theme)
        self._csc.colourScaleChanged.connect(catch_signal)
        self._csc.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._csc.exec()

    @classmethod
    def _slot_file_dialog_creator(cls) -> None:
        """ Shows the file dialog creator. """

        de = _FileDialogDataEditor()
        de.exec()

    @classmethod
    def _slot_mbt_creator(cls) -> None:
        """ Shows the MessageBoxType creator. """

        mbtc = _MessageBoxTypeCreator()
        mbtc.exec()

    @classmethod
    def _slot_theme_creator(cls) -> None:
        """ Shows the theme creator. """

        tc = ThemeCreator()
        tc.exec()


def creator_centre() -> None:
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _CreatorCentre()
    mainWindow.show()
    app.exec()
