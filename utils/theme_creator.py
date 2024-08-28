""" A module for a theme creator dialog. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
import sys

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules
from utils.colours import Colour, ColourSelector
from utils._general import SignalBlocker
from utils.theme import set_widget_theme, WidgetTheme


class _ColourSetter(QWidget):
    """ A widget for colour selection or manual colour setting. """

    def __init__(self):
        """ Class initializer. """

        super().__init__(parent=None)

        self._set_colour = QColor(255, 255, 255)

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkSelector = QCheckBox("Use selector")
        self._chkSelector.setChecked(True)
        self._lblColour = QLabel()
        self._set_colour_label()

        self._btnSelector = QPushButton("Open selector dialog")
        self._btnSelector.setFixedHeight(25)
        self._btnSelector.setObjectName('button')
        self._lblRGB = QLabel(text='RGB', parent=None)
        self._spblistRGB = [QSpinBox() for _ in range(3)]
        for spb in self._spblistRGB:
            spb.setRange(0, 255)
            spb.setValue(255)
            spb.setObjectName('spinbox')

        # Layouts
        self._vloSelector = QVBoxLayout()  # So the button is in line with...
        self._vloSelector.addWidget(self._btnSelector)  # ... everything else

        self._wdgSelector = QWidget()
        self._wdgSelector.setLayout(self._vloSelector)

        self._hloCustomColour = QHBoxLayout()
        self._hloCustomColour.addWidget(self._lblRGB)
        for spb in self._spblistRGB:
            self._hloCustomColour.addWidget(spb)

        self._wdgCustomColour = QWidget()
        self._wdgCustomColour.setLayout(self._hloCustomColour)

        self._sloStackedLayout = QStackedLayout()
        self._sloStackedLayout.addWidget(self._wdgSelector)
        self._sloStackedLayout.addWidget(self._wdgCustomColour)

        self._hloMainLayout = QHBoxLayout()
        self._hloMainLayout.addWidget(self._chkSelector)
        self._hloMainLayout.addWidget(self._lblColour)
        self._hloMainLayout.addLayout(self._sloStackedLayout)

        self.setLayout(self._hloMainLayout)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._chkSelector.stateChanged.connect(self._slot_update_selector)
        self._btnSelector.clicked.connect(self._slot_colour_selector)
        for spb in self._spblistRGB:
            spb.valueChanged.connect(self._update_colour)

    def _slot_update_selector(self) -> None:
        """ Updates which selector is shown based on the control checkbox. """

        if self._chkSelector.isChecked():
            self._sloStackedLayout.setCurrentIndex(0)
        else:
            self._sloStackedLayout.setCurrentIndex(1)

    def _set_colour_label(self) -> None:
        """ Sets the pixmap of the colour's display label. """

        pixmap = QPixmap(20, 20)
        pixmap.fill(self._set_colour)
        self._lblColour.setPixmap(pixmap)

    def _slot_colour_selector(self) -> None:
        """ Shows a colour selector dialog. """

        def catch_signal(button_id, colour) -> None:
            """ Catches the signal carrying the newly set colour.

            Parameters
            ----------
            button_id : int
                The caller button's ID, unused here.

            colour : Colour
                The colour to set.
            """

            self._set_colour = colour.as_qt()
            self._update_colour()

        cs = ColourSelector()
        cs.colourChanged.connect(catch_signal)
        cs.exec()

    def _update_colour(self) -> None:
        """ Updates the stored colour and its display label
        according to the sender. """

        if self.sender().objectName() == 'button':
            # Colour set in nested catch_signal()
            channels = {0: 'red', 1: 'green', 2: 'blue'}
            for idx, spb in enumerate(self._spblistRGB):
                with SignalBlocker(spb) as obj:
                    obj.setValue(getattr(self._set_colour, channels[idx])())
        elif self.sender().objectName() == 'spinbox':
            self._set_colour = QColor(*[s.value() for s in self._spblistRGB])

        self._set_colour_label()


class ThemeCreator(QDialog):
    """ A dialog for creating a custom widget theme / editing existing ones. """

    def __init__(self):
        """ Initializer for the class. """

        super().__init__(parent=None)

        self.setWindowTitle("Theme creator")

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        fields = "Window WindowText Base AlternateBase ToolTipBase "\
                 "ToolTipText Text Button ButtonText BrightText Link "\
                 "Highlight HighlightedText".split()
        self._lbllistFields = [QLabel(f) for f in fields]
        self._cslist = [_ColourSetter() for _ in range(len(fields))]

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._hlolistFields = [QHBoxLayout() for _ in range(len(fields))]
        for hlo, lbl, cs in zip(self._hlolistFields, self._lbllistFields,
                                self._cslist):
            hlo.addWidget(lbl)
            hlo.addWidget(cs)
            self._vloMainLayout.addLayout(hlo)

        self.setLayout(self._vloMainLayout)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        pass


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
        self._btnThemeCreator = QPushButton("Open a theme creator dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnThemeCreator)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnThemeCreator.clicked.connect(self._slot_tc_test)

    @staticmethod
    def _slot_tc_test() -> None:
        """ Tests the theme creator dialog. """

        tc = ThemeCreator()
        tc.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
