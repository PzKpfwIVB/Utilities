""" Customizable messageboxes with themes. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.0.5'


# Built-in modules
from dataclasses import dataclass, field, fields
import json
import os
import sys
from typing import Any, cast, Iterable

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom classes/modules
from utils_qt_mk.config import (_PACKAGE_DIR, mbt_file_path, _STUBS_DIR,
                                icon_file_path, theme_dir)

from utils_qt_mk.general import (SignalBlocker, Singleton, get_imports,
                                 get_functions, get_classes, stub_repr,
                                 qt_connect)
from utils_qt_mk.theme import set_widget_theme, WidgetTheme


MessageBoxType: _MessageBoxType | None = None
_MBCategories: _MessageBoxCategories | None = None
_StandardButtons: dict[int, QMessageBox.StandardButton] = \
    {idx: btn for idx, btn
     in enumerate(cast(Iterable[QMessageBox.StandardButton],
                       QMessageBox.StandardButton))}
_WindowTypes: dict[int, Qt.WindowType] = \
    {idx: typ for idx, typ
     in enumerate(cast(Iterable[Qt.WindowType], Qt.WindowType))}


def get_messagebox_types(fetch_data: bool = False) \
        -> list[str | _MessageBoxData]:
    """ Returns the available messagebox types.

    :param fetch_data: A flag requesting the _MessageBoxData objects themselves.
    The default is False.
    """

    if fetch_data:
        return [pd for pd in MessageBoxType._types.values()]
    else:
        return [key.lower() for key in MessageBoxType._types.keys()]


def merge_json(path: str) -> None:
    """
    Takes an external JSON messagebox type file and merges its contents to
    the package's own file. This way if you create messageboxes you can reuse
    them in another project.

    :param path: Path to the external JSON messagebox type file.
    """

    with open(mbt_file_path(), 'r') as f:
        package_data = json.load(f)

    package_data = {mbd['type_id']: _MessageBoxData.from_dict(mbd)
                    for mbd in package_data}

    with open(path, 'r') as f:
        external_data = json.load(f)

    external_data = {mbd['type_id']: _MessageBoxData.from_dict(mbd)
                     for mbd in external_data}

    for type_id, mbd_e in external_data.items():
        if all(mbd_e != mbd_p for mbd_p in package_data):
            package_data[type_id] = mbd_e

    package_data = [{'type_id': t_id, **pd.as_dict}
                    for t_id, pd in package_data.items()]

    with open(mbt_file_path(), 'w') as f:
        json.dump(package_data, f, indent=4)

    try:
        os.remove(os.path.join(_PACKAGE_DIR, 'message.pyi'))
    except FileNotFoundError:
        pass
    else:
        _init_module()  # Reinitialize the module so that types are reloaded


@dataclass
class _MessageBoxData:
    """ Settings defining the appearance of a QMessageBox.

    :param icon: The icon to set for the message box.
    :param title: The title to set for the message box window.
    :param text: The text content to set for the message box.
    :param buttons: A list of standard buttons to set for the message box.
    :param flags: A list of flags to set for the message box defining its
        behaviour.
    """

    icon: QMessageBox.Icon = QMessageBox.Icon.NoIcon
    title: str = ''
    text: str = ''
    buttons: list[QMessageBox.StandardButton] = None
    flags: list[Qt.WindowType] = None

    def __post_init__(self) -> None:
        """ Adds the correct default values where they are mutable. """

        if self.buttons is None:
            self.buttons = [QMessageBox.StandardButton.NoButton]

        if self.flags is None:
            self.flags = [Qt.WindowType.Dialog,
                          Qt.WindowType.MSWindowsFixedSizeDialogHint]

    def __eq__(self, other) -> bool:
        """ Custom comparison rule, comparing each field. """

        if not isinstance(other, _MessageBoxData):
            return False

        return all(getattr(self, f.name) == getattr(other, f.name)
                   for f in fields(self))

    def merged_bits(self, attr: str) \
            -> QMessageBox.StandardButton | Qt.WindowType:
        """ Merges the bits of either `buttons` or `flags` and returns.

        :param attr: The requested attribute (`buttons` or `flags`) as a string.

        :returns: An Enum subclass (concrete type based on `attr`) with the
            merged value.
        """

        bit_pattern = getattr(self, attr)
        ret_types = {'buttons': QMessageBox.StandardButton,
                     'flags': Qt.WindowType}

        merged = 0
        for bp in bit_pattern:
            merged |= bp

        return ret_types[attr](merged)

    @property
    def as_dict(self) -> dict:
        """ Returns the data content as a dictionary. """

        return {'icon': self.icon.value,
                'title': self.title,
                'text': self.text,
                'buttons': [btn.value for btn in self.buttons],
                'flags': [flag.value for flag in self.flags]}

    @classmethod
    def from_dict(cls, src: dict) -> _MessageBoxData:
        """ Returns an instance built from a dictionary.

        :param src: A dictionary containing data to build an instance,
            extracted from the handled JSON file.
        """

        buttons = [QMessageBox.StandardButton(id_) for id_ in src['buttons']]
        flags = [Qt.WindowType(id_) for id_ in src['flags']]

        return cls(QMessageBox.Icon(src['icon']), src['title'], src['text'],
                   buttons, flags)


@dataclass
class _MessageBoxCategories(metaclass=Singleton):  # Not Enum because...
    """
    A constant dataclass for holding parameters of the four basic
    categories of message boxes and an additional custom type.
    """

    critical: _MessageBoxData = field(init=False)  # ...the values are mutable
    information: _MessageBoxData = field(init=False)
    question: _MessageBoxData = field(init=False)
    warning: _MessageBoxData = field(init=False)
    custom: _MessageBoxData = field(init=False)

    def __post_init__(self) -> None:
        """ Creates mutable values after initialization. """

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
    """ A collection of predefined types of messagebox. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        self._types: dict[str, _MessageBoxData] | None = None
        self.import_types()

    def __getattr__(self, name: str) -> Any:
        """ Handles an attribute access request.

        :param name: The name of the requested attribute.

        :returns: A stored `_MessageBoxData` object or an attribute of the
            internal dictionary.
        """

        try:
            return getattr(self._types, name)  # dict attributes
        except AttributeError:
            return self._types[name]  # _MessageBoxData object

    def __setattr__(self, key: str, value: _MessageBoxData | None) -> None:
        """ Handles an attribute setting request.

        :param key: The name of the attribute whose value is to be set.
        :param value: The value to set for the attribute.
        """

        if key.startswith('_'):  # Avoiding infinite recursion with _types
            dict.__setattr__(self, key, value)
        else:
            self._types[key] = value

    def __setitem__(self, key: str, value: _MessageBoxData) -> None:
        """
        Sets a new set of message box data for the internal dictionary by
        accessing with '[]'.

        :param key: The type ID to set the data to.
        :param value: The message box data to set.
        """

        try:
            self._types[key] = value
        except TypeError:
            self._types = {key: value}

    def __delitem__(self, key: str) -> None:
        """ Deletes a set of message box data from the internal dictionary. """

        del self._types[key]
        if not self._types:
            self._types = None

    def import_types(self) -> None:
        """ Imports types from the handled JSON file. """

        try:
            with open(mbt_file_path(), 'r') as f:
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
            data.append({'type_id': type_id, **type_data.as_dict})

        with open(mbt_file_path(), 'w') as f:
            json.dump(data, f, indent=4)

    def is_empty(self) -> bool:
        """ Returns True if there are no defined types, False if there are. """

        return self._types is None or not self._types

    def converted_keys(self) -> list[str]:
        """
        Returns the keys converted to a list of space-separated and capitalized
        strings.
        """

        keys = self._types.keys()
        return [k.capitalize().replace('_', ' ') for k in keys]


class _OrderedSelectionList(QWidget):
    """ A widget where an ordered selection can be made from a combobox. """

    def __init__(self, list_name: str, items: list, add: str, remove: str) \
            -> None:
        """ Initializer for the class.

        :param list_name: String identifier of the list set to a label.
        :param items: A list of items to set for the combobox.
        :param add: Text to set for the add button.
        :param remove: Text to set for the remove button.
        """

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

        self._lblList = QLabel(text=self._list_name, parent=None)
        self._cmbItems = QComboBox()
        self._cmbItems.addItems(self._items.keys())  # type: ignore
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

        qt_connect(self._btnAdd.clicked, self._slot_add_item)
        qt_connect(self._btnRemove.clicked, self._slot_remove_item)

    def _slot_add_item(self) -> None:
        """ Adds the current item of the combobox to the selection list. """

        new_item = self._cmbItems.currentText()
        if new_item not in self.selection_str:
            self._lwSelection.addItem(new_item)

    def _slot_remove_item(self) -> None:
        """ Removes the currently selected item from the selection list. """

        if (idx := self._lwSelection.currentIndex().row()) >= 0:
            self._lwSelection.takeItem(idx)

    def set_selection(self, new_selection: list[str]) -> None:
        """ Resets the selection list by the provided items.

        :param new_selection: The new items to set to the selection list.
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
        """
        Returns the selection list encoded by the order of the source item list.
        """

        return [self._items[s] for s in self.selection_str]

    def setEnabled(self, new_state: bool) -> None:
        """ Sets the enabled state of the child widgets.

        :param new_state: The new enabled state to set.
        """

        self._lwSelection.setEnabled(new_state)
        self._cmbItems.setEnabled(new_state)
        self._btnAdd.setEnabled(new_state)
        self._btnRemove.setEnabled(new_state)


class _MessageBoxTypeCreator(QDialog):
    """
    A dialog for defining custom messagebox types / editing existing ones.
    """

    def __init__(self) -> None:
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
        self._chkUseExistingType = QCheckBox(text="Use existing type",
                                             parent=None)
        self._chkUseExistingType.setEnabled(not MessageBoxType.is_empty())
        self._chkUseExistingType.setObjectName('checkbox')

        self._cmbAvailableTypes = QComboBox()
        self._cmbAvailableTypes.setObjectName('types')
        if not MessageBoxType.is_empty():
            self._cmbAvailableTypes.addItems(MessageBoxType.converted_keys())

        self._ledTypeID = QLineEdit()
        self._ledTypeID.setPlaceholderText("Type ID")

        self._lblCategory = QLabel(text='Category', parent=None)
        self._cmbCategories = QComboBox()
        self._cmbCategories.setObjectName('categories')
        self._cmbCategories.addItems(self._categories)
        self._cmbCategories.setObjectName('combobox')

        self._lblIcon = QLabel(text='Icon', parent=None)
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

        qt_connect(self._chkUseExistingType.stateChanged,
                   self._slot_set_control_states)
        qt_connect(self._cmbAvailableTypes.currentIndexChanged,
                   self._slot_update_by_combobox)
        qt_connect(self._cmbCategories.currentIndexChanged,
                   self._slot_set_control_states)
        qt_connect(self._btnTest.clicked, self._slot_test_settings)
        qt_connect(self._btnExport.clicked, self._slot_export_settings)
        qt_connect(self._btnDelete.clicked, self._slot_delete_settings)

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

    def _slot_update_by_combobox(self) -> None:
        """ Updates the dialog according to the controlling combobox. """

        typ = self._cmbAvailableTypes.currentText().lower().replace(' ', '_')
        mbd: _MessageBoxData = getattr(MessageBoxType, typ)

        self._cmbIcons.setCurrentIndex(mbd.icon.value)
        self._ledTitle.setText(mbd.title)
        self._tedText.setText(mbd.text)
        self._oslButtons.set_selection(
            [btn.name for btn in mbd.buttons])  # type: ignore
        self._oslFlags.set_selection(
            [f.name for f in mbd.flags])  # type: ignore

    def _get_as_messageboxdata(self) -> _MessageBoxData:
        """
        Returns a MessageBoxData object built from the settings made in the
        dialog.
        """

        buttons = [_StandardButtons[idx]
                   for idx in self._oslButtons.selection_idx]
        flags = [_WindowTypes[idx] for idx in self._oslFlags.selection_idx]
        return _MessageBoxData(QMessageBox.Icon(self._cmbIcons.currentIndex()),
                               self._ledTitle.text(),
                               self._tedText.toPlainText(),
                               buttons,
                               flags)

    def _slot_test_settings(self) -> None:
        """ Creates a message box dialog based on the settings. """

        retval = message(self, self._get_as_messageboxdata())
        print(f"The message box returned {retval} "
              f"({QMessageBox.StandardButton(retval).name}).")

    def _slot_export_settings(self) -> None:
        """
        Exports the currently set type and updates the dialog accordingly.
        """

        if self._chkUseExistingType.isChecked():
            type_id = (self._cmbAvailableTypes.currentText().lower()
                       .replace(' ', '_'))
        else:
            type_id = self._ledTypeID.text().lower().replace(' ', '_')

        # Data updated, no need to reimport
        MessageBoxType[type_id] = self._get_as_messageboxdata()
        MessageBoxType.export_types()
        with SignalBlocker(self._cmbAvailableTypes) as obj:
            obj.clear()
            obj.addItems(MessageBoxType.converted_keys())
            obj.setCurrentIndex(obj.count() - 1)

        self._chkUseExistingType.setEnabled(True)

    def _slot_delete_settings(self) -> None:
        """
        Deletes the currently selected type and updates the dialog accordingly.
        """

        type_id = (self._cmbAvailableTypes.currentText().lower()
                   .replace(' ', '_'))
        del MessageBoxType[type_id]
        with SignalBlocker(self._cmbAvailableTypes) as obj:
            obj.clear()
            if MessageBoxType.is_empty():
                os.remove('messagebox_types.json')
            else:
                MessageBoxType.export_types()
                obj.addItems(MessageBoxType.converted_keys())
                obj.setCurrentIndex(obj.count() - 1)

        self._slot_update_by_combobox()  # One update after signal got unblocked

        if MessageBoxType.is_empty():
            with SignalBlocker(self._chkUseExistingType) as obj:
                obj.setEnabled(False)


def message(parent: QWidget, mbd: _MessageBoxData, custom_text: str = None) \
        -> QMessageBox.StandardButton:
    """
    Shows a modal QMessageBox with preset content (or custom text) and a custom
    theme.

    :param parent: The parent widget calling for the message dialog.
    :param mbd: MessageBox data to define the appearance of the created window.
    :param custom_text: Overrides the preset text. The default is None, having
        no effect.

    :returns: The clicked standard button (or its equal if the dialog was just
        closed).
    """

    default = os.listdir(theme_dir())[0].split('/')[-1].split('.')[0]
    theme = getattr(WidgetTheme, default)

    try:
        theme = parent.theme  # type: ignore
    except AttributeError:
        print(f"Cannot access the theme of the parent object of class "
              f"'{parent.__class__.__name__}' or it has no theme. "
              f"Using the default theme ({default}).")

    text = mbd.text if custom_text is None else custom_text
    messagebox = QMessageBox(mbd.icon, mbd.title, text,
                             mbd.merged_bits('buttons'), parent,
                             mbd.merged_bits('flags'))

    if icon_file_path():
        messagebox.setWindowIcon(QIcon(icon_file_path()))  # type: ignore

    set_widget_theme(messagebox, theme)
    messagebox.setWindowModality(Qt.WindowModality.ApplicationModal)
    return QMessageBox.StandardButton(messagebox.exec())


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

        qt_connect(self._btnMBTCreator.clicked, self._slot_mbtc_test)

    @classmethod
    def _slot_mbtc_test(cls) -> None:
        """ Tests the MessageBoxType creator dialog. """

        mbtc = _MessageBoxTypeCreator()
        mbtc.exec()


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
        if cls == _MessageBoxType:
            try:
                with open(mbt_file_path(), 'r') as f:
                    data: list[dict] = json.load(f)

                extra_cvs = '\n'.join(
                    [f"\t{entry['type_id']}: _MessageBoxData "
                     "= None" for entry in data])
            except FileNotFoundError:
                extra_cvs = None
        else:
            extra_cvs = None

        class_reprs.append(
            stub_repr(cls, signals=sigs, extra_cvs=extra_cvs))

    reprs.append('\n\n'.join(class_reprs))

    with open(stub_path, 'w') as f:
        f.write(imports)
        f.write("MessageBoxType: _MessageBoxType = None\n")
        f.write("_MBCategories: _MessageBoxCategories = None\n")
        f.write("_StandardButtons: dict[int, QMessageBox.StandardButton] "
                "= None\n")
        f.write("_WindowTypes: dict[int, Qt.WindowType] = None\n\n")
        f.write(''.join(reprs))


def _init_module() -> None:
    """ Initializes the module. """

    write_stub()

    global MessageBoxType
    MessageBoxType = _MessageBoxType()

    global _MBCategories
    _MBCategories = _MessageBoxCategories()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()

