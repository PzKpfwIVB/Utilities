""" Customizable messageboxes with themes. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.0.0'


# Built-in modules
from dataclasses import dataclass, field
import json
import os
import sys
from typing import Iterable, cast

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom classes/modules
from utils._general import SignalBlocker, Singleton
from utils.theme import set_widget_theme, WidgetTheme


MessageBoxType: _MessageBoxType | None = None
_MBCategories: _MessageBoxCategories | None = None
_StandardButtons: dict[int, QMessageBox.StandardButton] = \
    {idx: btn for idx, btn
     in enumerate(cast(Iterable[QMessageBox.StandardButton],
                       QMessageBox.StandardButton))}
_WindowTypes: dict[int, Qt.WindowType] = \
    {idx: typ for idx, typ
     in enumerate(cast(Iterable[Qt.WindowType], Qt.WindowType))}


@dataclass
class _MessageBoxData:
    icon: QMessageBox.Icon = QMessageBox.Icon.NoIcon
    title: str = ''
    text: str = ''
    buttons: list[QMessageBox.StandardButton] = None
    flags: list[Qt.WindowType] = None

    def __post_init__(self):
        """ Add the correct default values where they are mutable. """

        if self.buttons is None:
            self.buttons = [QMessageBox.StandardButton.NoButton]

        if self.flags is None:
            self.flags = [Qt.WindowType.Dialog,
                          Qt.WindowType.MSWindowsFixedSizeDialogHint]

    def as_dict(self) -> dict:
        """ Returns the data content as a dictionary. """

        return {'icon': self.icon.value,
                'title': self.title,
                'text': self.text,
                'buttons': [btn.value for btn in self.buttons],
                'flags': [flag.value for flag in self.flags]}

    @classmethod
    def from_dict(cls, src) -> _MessageBoxData:
        """ Returns an instance built from a dictionary.

        Parameters
        ----------
        src : dict
            A dictionary containing data to build an instance,
            extracted from the handled JSON file.
        """

        buttons = [QMessageBox.StandardButton(id_) for id_ in src['buttons']]
        flags = [Qt.WindowType(id_) for id_ in src['flags']]

        return cls(QMessageBox.Icon(src['icon']), src['title'], src['text'],
                   buttons, flags)


@dataclass
class _MessageBoxCategories(metaclass=Singleton):  # Not Enum because...
    critical: _MessageBoxData = field(init=False)  # ...the values are mutable
    information: _MessageBoxData = field(init=False)
    question: _MessageBoxData = field(init=False)
    warning: _MessageBoxData = field(init=False)
    custom: _MessageBoxData = field(init=False)

    def __post_init__(self):
        """ Creating mutable values after initialization. """

        self.critical = _MessageBoxData(QMessageBox.Icon.Critical,
                                        buttons=[QMessageBox.StandardButton.Ok])
        self.information = _MessageBoxData(QMessageBox.Icon.Information,
                                           buttons=
                                           [QMessageBox.StandardButton.Ok])
        self.question = _MessageBoxData(QMessageBox.Icon.Question,
                                        buttons=[QMessageBox.StandardButton.Yes,
                                                 QMessageBox.StandardButton.No])
        self.warning = _MessageBoxData(QMessageBox.Icon.Warning,
                                       buttons=[QMessageBox.StandardButton.Ok])
        self.custom = _MessageBoxData()


class _MessageBoxType(metaclass=Singleton):
    """ A predefined type of messagebox. """

    def __init__(self):
        self._types: dict[str, _MessageBoxData] | None = None
        self.import_types()

    def __getattr__(self, name):
        try:
            return getattr(self._types, name)  # dict attributes
        except AttributeError:
            return self._types[name]  # _MessageBoxData object

    def __setattr__(self, key, value):
        if key.startswith('_'):  # Avoiding infinite recursion with _types
            dict.__setattr__(self, key, value)
        else:
            self._types[key] = value

    def __setitem__(self, key, value):
        try:
            self._types[key] = value
        except TypeError:
            self._types = {key: value}

    def __delitem__(self, key):
        del self._types[key]
        if not self._types:
            self._types = None

    def import_types(self) -> None:
        """ Imports types from the handled JSON file. """

        try:
            with open('./messagebox_types.json', 'r') as f:
                data: list[dict] = json.load(f)

            self._types = {}
            for entry in data:
                type_id = entry.pop('type_id')
                self._types[type_id] = _MessageBoxData.from_dict(entry)
        except FileNotFoundError:
            pass

    def export_types(self) -> None:
        """ Exports types to the handled JSON file. """

        data = []
        for type_id, type_data in self._types.items():
            data.append({'type_id': type_id, **type_data.as_dict()})

        with open('./messagebox_types.json', 'w') as f:
            json.dump(data, f, indent=4)

    def is_empty(self) -> bool:
        """ Returns True if there are no defined types, False if there are. """

        return self._types is None or not self._types


class _OrderedSelectionList(QWidget):
    """ A widget where an ordered selection can be made from a combobox. """

    def __init__(self, list_name, items, add, remove):
        super().__init__(parent=None)

        self._list_name = list_name
        self._items = {item: idx for idx, item in enumerate(items)}
        self._add = add
        self._remove = remove

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._lwSelection = QListWidget()
        self._lwSelection.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove)

        self._lblList = QLabel(self._list_name)
        self._cmbItems = QComboBox()
        self._cmbItems.addItems(self._items.keys())
        self._btnAdd = QPushButton(self._add)
        self._btnRemove = QPushButton(self._remove)

        # Layouts
        self._vloControls = QVBoxLayout()
        self._vloControls.addWidget(self._lblList)
        self._vloControls.addWidget(self._cmbItems)
        self._vloControls.addWidget(self._btnAdd)
        self._vloControls.addWidget(self._btnRemove)
        self._vloControls.addStretch(0)

        self._hloMainLayout = QHBoxLayout()
        self._hloMainLayout.addWidget(self._lwSelection)
        self._hloMainLayout.addLayout(self._vloControls)

        self.setLayout(self._hloMainLayout)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnAdd.clicked.connect(self._slot_add_item)
        self._btnRemove.clicked.connect(self._slot_remove_item)

    def _slot_add_item(self) -> None:
        """ Adds the current item of the combobox to the selection list. """

        new_item = self._cmbItems.currentText()
        if new_item not in self.selection_str:
            self._lwSelection.addItem(new_item)

    def _slot_remove_item(self) -> None:
        """ Removes the currently selected item from the selection list. """

        if (idx := self._lwSelection.currentIndex().row()) >= 0:
            self._lwSelection.takeItem(idx)

    def set_selection(self, new_selection) -> None:
        """ Resets the selection list by the provided items.

        Parameters
        ----------
        new_selection : list[str]
            The new items to set to the selection list.
        """

        self._lwSelection.clear()
        for item in new_selection:
            if item in self._items.keys():
                self._lwSelection.addItem(item)

    @property
    def selection_str(self) -> list[str]:
        """ Returns the string content of the selection list. """

        return [self._lwSelection.item(i).text()
                for i in range(self._lwSelection.count())]

    @property
    def selection_idx(self) -> list[int]:
        """ Returns the selection list encoded by the
        order of the source item list. """

        return [self._items[s] for s in self.selection_str]

    def setEnabled(self, new_state):
        """ Sets the enabled state of the child widgets.

        Parameters
        ----------
        new_state : bool
            The new enabled state to set.
        """

        self._lwSelection.setEnabled(new_state)
        self._cmbItems.setEnabled(new_state)
        self._btnAdd.setEnabled(new_state)
        self._btnRemove.setEnabled(new_state)


class _MessageBoxTypeCreator(QDialog):
    """ A dialog for defining custom messagebox types /
     editing existing ones. """

    def __init__(self):
        """ Initializer for the class. """

        super().__init__(parent=None)

        self.setWindowTitle("MBT Creator")

        self._categories = ("critical information question "
                            "warning custom".split())

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkUseExistingType = QCheckBox("Use existing type")
        self._chkUseExistingType.setChecked(not MessageBoxType.is_empty())

        self._cmbAvailableTypes = QComboBox()
        self._cmbAvailableTypes.setObjectName('types')
        if not MessageBoxType.is_empty():
            keys = [key.capitalize().replace('_', ' ')
                    for key in MessageBoxType.keys()]
            self._cmbAvailableTypes.addItems(keys)

        self._ledTypeID = QLineEdit()
        self._ledTypeID.setPlaceholderText("Type ID")

        self._lblCategory = QLabel('Category')
        self._cmbCategories = QComboBox()
        self._cmbCategories.setObjectName('categories')
        self._cmbCategories.addItems(self._categories)

        self._lblIcon = QLabel('Icon')
        self._cmbIcons = QComboBox()
        self._cmbIcons.addItems([icon.name for icon in QMessageBox.Icon])

        self._ledTitle = QLineEdit()
        self._ledTitle.setPlaceholderText("Window title")
        self._tedText = QTextEdit()
        self._tedText.setPlaceholderText('Message')

        buttons = [btn.name for btn in _StandardButtons.values()]
        self._oslButtons = _OrderedSelectionList('Buttons',
                                                 buttons,
                                                 "Add button",
                                                 "Remove button")

        flags = [wt.name for wt in Qt.WindowType]
        self._oslFlags = _OrderedSelectionList('Flags',
                                               flags,
                                               "Add flag",
                                               "Remove flag")

        self._btnTest = QPushButton("Show test message")
        self._btnExport = QPushButton("Export type")
        self._btnDelete = QPushButton("Delete type")

        # Layouts
        self._hloExistingTypes = QHBoxLayout()
        self._hloExistingTypes.addWidget(self._chkUseExistingType)
        self._hloExistingTypes.addWidget(self._cmbAvailableTypes)

        self._hloCategory = QHBoxLayout()
        self._hloCategory.addWidget(self._lblCategory)
        self._hloCategory.addWidget(self._cmbCategories)

        self._hloIcon = QHBoxLayout()
        self._hloIcon.addWidget(self._lblIcon)
        self._hloIcon.addWidget(self._cmbIcons)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addLayout(self._hloExistingTypes)
        self._vloMainLayout.addWidget(self._ledTypeID)
        self._vloMainLayout.addLayout(self._hloCategory)
        self._vloMainLayout.addLayout(self._hloIcon)
        self._vloMainLayout.addWidget(self._ledTitle)
        self._vloMainLayout.addWidget(self._tedText)
        self._vloMainLayout.addWidget(self._oslButtons)
        self._vloMainLayout.addWidget(self._oslFlags)
        self._vloMainLayout.addWidget(self._btnTest)
        self._vloMainLayout.addWidget(self._btnExport)
        self._vloMainLayout.addWidget(self._btnDelete)
        self._vloMainLayout.addStretch(0)

        self.setLayout(self._vloMainLayout)

        # Further initialization
        self._slot_set_control_states()

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._chkUseExistingType.stateChanged.connect(
            self._slot_set_control_states)
        # self._cmbAvailableTypes.currentIndexChanged.connect(
        #     self._slot_update_by_combobox)
        self._cmbCategories.currentIndexChanged.connect(
            self._slot_set_control_states)
        # self._btnTest.clicked.connect(self._slot_test_settings)
        self._btnExport.clicked.connect(self._slot_export_settings)
        self._btnDelete.clicked.connect(self._slot_delete_settings)

    def _slot_set_control_states(self) -> None:
        """ Updates the controls' enabled state based on the state of
                the checkbox. """

        use_existing_type = self._chkUseExistingType.isChecked()
        standard = self._cmbCategories.currentText() != 'custom'

        self._cmbAvailableTypes.setEnabled(use_existing_type)
        self._ledTypeID.setVisible(not use_existing_type)
        self._cmbCategories.setEnabled(not use_existing_type)

        self._cmbIcons.setEnabled(not use_existing_type and not standard)
        self._ledTitle.setEnabled(not use_existing_type)
        self._tedText.setEnabled(not use_existing_type)
        self._oslButtons.setEnabled(not use_existing_type and not standard)
        self._oslFlags.setEnabled(not use_existing_type and not standard)

        self._btnExport.setEnabled(not use_existing_type)
        self._btnDelete.setEnabled(use_existing_type)

        if not use_existing_type:
            mbd = getattr(_MBCategories, self._cmbCategories.currentText())
        else:
            key = (self._cmbAvailableTypes.currentText()
                   .lower().replace(' ', '_'))
            mbd = getattr(MessageBoxType, key)

        self._cmbIcons.setCurrentIndex(mbd.icon.value)
        self._ledTitle.setText(mbd.title)
        self._tedText.setText(mbd.text)
        self._oslButtons.set_selection([btn.name for btn in mbd.buttons])
        self._oslFlags.set_selection([flag.name for flag in mbd.flags])

    def _slot_export_settings(self) -> None:
        """ Exports the currently set type and updates the
        dialog accordingly. """

        buttons = [_StandardButtons[idx]
                   for idx in self._oslButtons.selection_idx]
        flags = [_WindowTypes[idx] for idx in self._oslFlags.selection_idx]
        mbd = _MessageBoxData(QMessageBox.Icon(self._cmbIcons.currentIndex()),
                              self._ledTitle.text(),
                              self._tedText.toPlainText(),
                              buttons,
                              flags)

        if self._chkUseExistingType.isChecked():
            type_id = (self._cmbAvailableTypes.currentText().lower()
                       .replace(' ', '_'))
        else:
            type_id = self._ledTypeID.text().lower().replace(' ', '_')

        MessageBoxType[type_id] = mbd  # Data updated, no need to reimport
        MessageBoxType.export_types()
        with SignalBlocker(self._cmbAvailableTypes) as obj:
            obj.clear()
            keys = [key.capitalize().replace('_', ' ')
                    for key in MessageBoxType.keys()]
            obj.addItems(keys)
            obj.setCurrentIndex(obj.count() - 1)

        self._chkUseExistingType.setChecked(True)

    def _slot_delete_settings(self):
        """ Deletes the currently selected type and
        updates the dialog accordingly. """

        type_id = (self._cmbAvailableTypes.currentText().lower()
                   .replace(' ', '_'))
        del MessageBoxType[type_id]
        with SignalBlocker(self._cmbAvailableTypes) as obj:
            obj.clear()
            if MessageBoxType.is_empty():
                os.remove('./messagebox_types.json')
            else:
                MessageBoxType.export_types()
                obj.addItems(MessageBoxType.keys())
                obj.setCurrentIndex(obj.count() - 1)

        if MessageBoxType.is_empty():
            with SignalBlocker(self._chkUseExistingType) as obj:
                obj.setChecked(False)


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
        self._btnMBTCreator = QPushButton("Open a MessageBoxType "
                                          "creator dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnMBTCreator)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnMBTCreator.clicked.connect(self._slot_mbtc_test)

    @staticmethod
    def _slot_mbtc_test() -> None:
        """ Tests the MessageBoxType creator dialog. """

        mbtc = _MessageBoxTypeCreator()
        mbtc.exec()


def _init_module() -> None:
    """ Initializes the module. """

    global MessageBoxType
    MessageBoxType = _MessageBoxType()

    global _MBCategories
    _MBCategories = _MessageBoxCategories()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()

