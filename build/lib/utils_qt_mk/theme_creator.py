""" A module for a theme creator dialog. """

__author__ = "Mihaly Konda"
__version__ = '1.0.5'

# Built-in modules
from dataclasses import fields
import os
import sys

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules
from utils_qt_mk.config import _PACKAGE_DIR, _STUBS_DIR, theme_dir
_THEME_DIR = theme_dir()

from utils_qt_mk.colours import ColourSelector, set_extended_default
from utils_qt_mk.custom_file_dialog import custom_dialog, CFDType
from utils_qt_mk.general import (SignalBlocker, get_imports, get_functions,
                                 get_classes, stub_repr, qt_connect)
from utils_qt_mk.theme import set_widget_theme, ThemeParameters, WidgetTheme


set_extended_default(True)  # To show the extended selector by default


class _ColourSetter(QWidget):
    """ A widget for colour selection or manual colour setting. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

        self._set_colour = QColor(255, 255, 255)  # type: ignore

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkSelector = QCheckBox(text="Use selector", parent=None)
        self._chkSelector.setChecked(True)
        self._lblColour = QLabel(parent=None)
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
        self._vloSelector.setContentsMargins(0, 0, 0, 0)
        self._vloSelector.setSpacing(0)

        self._wdgSelector = QWidget()
        self._wdgSelector.setLayout(self._vloSelector)

        self._hloCustomColour = QHBoxLayout()
        self._hloCustomColour.addWidget(self._lblRGB)
        for spb in self._spblistRGB:
            self._hloCustomColour.addWidget(spb)

        self._hloCustomColour.setContentsMargins(0, 0, 0, 0)
        self._hloCustomColour.setSpacing(0)

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

        qt_connect(self._chkSelector.stateChanged, self._slot_update_selector)
        qt_connect(self._btnSelector.clicked, self._slot_colour_selector)
        for spb in self._spblistRGB:
            qt_connect(spb.valueChanged, self._update_colour)

    @property
    def colour(self) -> QColor:
        """ Returns the stored colour. """

        return self._set_colour

    @colour.setter
    def colour(self, new_colour: QColor) -> None:
        """ Updates the stored colour and its associated widgets.

        :param new_colour: The new colour to set.
        """

        self._set_colour = new_colour
        self._update_spinboxes()
        self._set_colour_label()

    def set_enabled(self, new_state: bool) -> None:
        """ Sets the enabled state of the controls.

        :param new_state: The new enabled state to set.
        """

        self._chkSelector.setEnabled(new_state)
        self._btnSelector.setEnabled(new_state)
        for spb in self._spblistRGB:
            spb.setEnabled(new_state)

    def _slot_update_selector(self) -> None:
        """ Updates which selector is shown based on the control checkbox. """

        if self._chkSelector.isChecked():
            self._sloStackedLayout.setCurrentIndex(0)
        else:
            self._sloStackedLayout.setCurrentIndex(1)

    def _set_colour_label(self) -> None:
        """ Sets the pixmap of the colour's display label. """

        pixmap = QPixmap(20, 20)  # type: ignore
        pixmap.fill(self._set_colour)
        self._lblColour.setPixmap(pixmap)

    def _slot_colour_selector(self) -> None:
        """ Shows a colour selector dialog. """

        def catch_signal(button_id, colour) -> None:
            """ Catches the signal carrying the newly set colour.

            :param button_id: The caller button's ID, unused here.
            :param colour: The colour to set.
            """

            self._set_colour = colour.as_qt()
            self._update_colour()

        cs = ColourSelector()
        cs.colourChanged.connect(catch_signal)
        cs.exec()

    def _update_spinboxes(self) -> None:
        """ Updates the values of spinboxes by the stored colour. """

        channels = {0: 'red', 1: 'green', 2: 'blue'}
        for idx, spb in enumerate(self._spblistRGB):
            with SignalBlocker(spb) as obj:
                obj.setValue(getattr(self._set_colour, channels[idx])())

    def _update_colour(self) -> None:
        """
        Updates the stored colour and its display label according to the sender.
        """

        if self.sender().objectName() == 'button':
            # Colour set in nested catch_signal()
            self._update_spinboxes()
        elif self.sender().objectName() == 'spinbox':
            self._set_colour = QColor(
                *[s.value() for s in self._spblistRGB])  # type: ignore

        self._set_colour_label()


class _ThemePreview(QWidget):
    """ A widget for previewing a theme. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._lblTest = QLabel(text="Test label (with tooltip)", parent=None)
        self._lblTest.setToolTip("Test tooltip")
        self._cmbTest = QComboBox(parent=None)
        self._cmbTest.addItems(["Item 1", "Item 2", "Item 3"])
        self._chkTest = QCheckBox(text="Test checkbox", parent=None)
        self._chkTest.setTristate(True)
        self._ledTest = QLineEdit()
        self._ledTest.setPlaceholderText('Placeholder')
        self._ledTest2 = QLineEdit()
        self._ledTest2.setText("Test text")
        self._ledTest2.setSelection(5, 4)
        self._btnTest = QPushButton("Test button")
        self._sldTest = QSlider(Qt.Orientation.Horizontal, parent=None)
        self._sldTest.setValue(50)
        self._pbTest = QProgressBar(parent=None)
        self._pbTest.setValue(35)
        self._pbTest2 = QProgressBar(parent=None)
        self._pbTest2.setValue(85)

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._lblTest)
        self._vloMainLayout.addWidget(self._cmbTest)
        self._vloMainLayout.addWidget(self._chkTest)
        self._vloMainLayout.addWidget(self._ledTest)
        self._vloMainLayout.addWidget(self._ledTest2)
        self._vloMainLayout.addWidget(self._btnTest)
        self._vloMainLayout.addWidget(self._sldTest)
        self._vloMainLayout.addWidget(self._pbTest)
        self._vloMainLayout.addWidget(self._pbTest2)

        self.setLayout(self._vloMainLayout)


class ThemeCreator(QDialog):
    """ A dialog for creating a custom widget theme / editing existing ones. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

        self.setWindowTitle("Theme creator")

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkUseExistingTheme = QCheckBox(text="Use existing theme",
                                              parent=None)
        self._chkUseExistingTheme.setChecked(True)
        themes = [fn.capitalize().split('.')[0]
                  for fn in os.listdir(_THEME_DIR)]

        self._cmbAvailableThemes = QComboBox()
        self._cmbAvailableThemes.addItems(themes)

        self._fields = "Window WindowText Base AlternateBase ToolTipBase "\
                       "ToolTipText Text Button ButtonText BrightText "\
                       "Highlight HighlightedText".split()
        self._lbllistFields = [QLabel(f) for f in self._fields]
        self._cslist = [_ColourSetter()
                        for _ in range(len(self._fields))]
        self._btnUpdate = QPushButton("Update preview")
        self._btnExport = QPushButton(
            "Export theme (name should be in lowercase)")
        self._btnDelete = QPushButton("Delete theme")
        self._tpPreview = _ThemePreview()

        # Layouts
        self._hloExistingThemes = QHBoxLayout()
        self._hloExistingThemes.addWidget(self._chkUseExistingTheme)
        self._hloExistingThemes.addWidget(self._cmbAvailableThemes)

        self._vloThemeControls = QVBoxLayout()
        self._vloThemeControls.addLayout(self._hloExistingThemes)
        self._hlolistFields = [QHBoxLayout() for _ in range(
            len(self._fields))]
        for hlo, lbl, cs in zip(self._hlolistFields,
                                self._lbllistFields,
                                self._cslist):
            hlo.addWidget(lbl)
            hlo.addStretch(0)
            hlo.addWidget(cs)
            self._vloThemeControls.addLayout(hlo)

        self._vloThemeControls.addWidget(self._btnUpdate)
        self._vloThemeControls.addWidget(self._btnExport)
        self._vloThemeControls.addWidget(self._btnDelete)
        self._vloThemeControls.addStretch(0)

        self._vloPreview = QVBoxLayout()
        self._vloPreview.addWidget(self._tpPreview)
        self._vloPreview.addStretch(0)

        self._hloMainLayout = QHBoxLayout()
        self._hloMainLayout.addLayout(self._vloThemeControls)
        self._hloMainLayout.addLayout(self._vloPreview)

        self.setLayout(self._hloMainLayout)

        # Further initialization
        self._slot_use_existing_theme()
        self._slot_update_by_combobox(0)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._chkUseExistingTheme.stateChanged,
                   self._slot_use_existing_theme)
        qt_connect(self._cmbAvailableThemes.currentIndexChanged,
                   self._slot_update_by_combobox)
        qt_connect(self._btnUpdate.clicked, self._slot_update_by_custom_colours)
        qt_connect(self._btnExport.clicked, self._slot_export_theme)
        qt_connect(self._btnDelete.clicked, self._slot_delete_theme)

    def _slot_use_existing_theme(self) -> None:
        """
        Updates the controls' enabled state based on the state of the checkbox.
        """

        use_existing_theme = self._chkUseExistingTheme.isChecked()
        self._cmbAvailableThemes.setEnabled(use_existing_theme)
        for cs in self._cslist:
            cs.set_enabled(not use_existing_theme)

        self._btnUpdate.setEnabled(not use_existing_theme)
        self._btnExport.setEnabled(not use_existing_theme)
        self._btnDelete.setEnabled(use_existing_theme)

        if use_existing_theme:  # To reset to the theme set in the combobox
            theme_idx = self._cmbAvailableThemes.currentIndex()
            self._slot_update_by_combobox(theme_idx)

    def _slot_update_by_combobox(self, index: int) -> None:
        """ Updates the preview based on the selection made in the combobox.

        :param index: The index of the item selected in the combobox.
        """

        theme_name = self._cmbAvailableThemes.itemText(index).lower()
        theme = getattr(WidgetTheme, theme_name)
        for f in fields(theme):
            try:
                field_idx = self._fields.index(f.name)
            except ValueError:
                pass  # Skipping src_path
            else:
                self._cslist[field_idx].colour = getattr(theme, f.name)

        set_widget_theme(self, theme)

    def _slot_update_by_custom_colours(self) -> None:
        """ Updates the preview based on the set custom colours. """

        theme = ThemeParameters()
        for attr, cs in zip(self._fields, self._cslist):
            setattr(theme, attr, cs.colour)

        set_widget_theme(self, theme)

    def _slot_export_theme(self) -> None:
        """
        Exports the currently set custom theme and updates the dialog
        accordingly.
        """

        theme = ThemeParameters()
        colour_attrs = [f.name for f in fields(theme) if f.name != 'src_file']
        for attr, cs in zip(colour_attrs, self._cslist):
            setattr(theme, attr, cs.colour)

        success, path = custom_dialog(self, CFDType.destination_themes)
        if success:
            new_theme = path.split('/')[-1].split('.')[0].capitalize()
            theme.write_json(path)
            WidgetTheme.load_dict()
            with SignalBlocker(self._cmbAvailableThemes) as obj:
                self._cmbAvailableThemes.clear()
                themes = [fn.capitalize().split('.')[0]
                          for fn in os.listdir(_THEME_DIR)]
                obj.addItems(themes)
                obj.setCurrentIndex(themes.index(new_theme))

            self._chkUseExistingTheme.setChecked(True)

    def _slot_delete_theme(self) -> None:
        """ Deletes the currently viewed theme's JSON file and
        updates the dialog accordingly. """

        theme = self._cmbAvailableThemes.currentText().lower()
        os.remove(os.path.join(_THEME_DIR, f'{theme}.json'))
        WidgetTheme.load_dict()
        with SignalBlocker(self._cmbAvailableThemes) as obj:
            self._cmbAvailableThemes.clear()
            themes = [fn.capitalize().split('.')[0]
                      for fn in os.listdir(_THEME_DIR)]
            obj.addItems(themes)
            obj.setCurrentIndex(0)


class _TestApplication(QMainWindow):
    """ The entry point for testing. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

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

        qt_connect(self._btnThemeCreator.clicked, self._slot_tc_test)

    @classmethod
    def _slot_tc_test(cls) -> None:
        """ Tests the theme creator dialog. """

        tc = ThemeCreator()
        tc.exec()


def write_stub() -> None:
    """ Writes the stub file to the project directory if it doesn't exist
    already or if an external stub file directory is set it creates a new stub
    file there (and deletes the package's own) or overrides the existing one.
    """

    if getattr(sys, 'frozen', False):
        return  # Disable in built app

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    if _STUBS_DIR:
        stub_path = os.path.join(_STUBS_DIR, f'{script_name}.pyi')
        package_stub_path = os.path.join(_PACKAGE_DIR, f'{script_name}.pyi')
        if os.path.exists(package_stub_path):
            os.remove(package_stub_path)
    else:
        stub_path = os.path.join(_PACKAGE_DIR, f'{script_name}.pyi')
        if os.path.exists(stub_path):
            return

    imports = get_imports(__file__)

    functions = [globals().get(func_name) for func_name
                 in get_functions(__file__, ignores=['_init_module'])]

    reprs = [stub_repr(func) for func in functions]
    reprs.append('\n\n')

    class_reprs = []
    classes = {globals().get(cls_name): signals
               for cls_name, signals in get_classes(__file__).items()}

    for cls, sigs in classes.items():
        add_getattr = not cls.__name__.startswith('_')
        class_reprs.append(stub_repr(cls, signals=sigs,
                                     add_getattr=add_getattr))

    reprs.append('\n\n'.join(class_reprs))

    repr_ = f"{imports}{''.join(reprs)}"

    with open(stub_path, 'w') as f:
        f.write(repr_)


def _init_module() -> None:
    """ Initializes the module. """

    write_stub()

_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
