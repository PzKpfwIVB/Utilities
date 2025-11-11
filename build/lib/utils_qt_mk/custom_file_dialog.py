""" File dialogs customized by a JSON file. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.0.8'


# Built-in modules
import os
from dataclasses import dataclass, fields
import json
import sys

# Qt6 modules
from PySide6.QtWidgets import *

# Custom modules
from utils_qt_mk.config import _PACKAGE_DIR, _STUBS_DIR, cfd_data_file_path
from utils_qt_mk.general import (SignalBlocker, Singleton, get_imports,
                                 get_functions, get_classes, stub_repr,
                                 qt_connect)


CFDType: _CFDType | None = None


def get_cfd_types(fetch_data: bool = False) -> list[str | CFDData]:
    """ Returns the available custom file dialog (CFD) types.

    :param fetch_data: A flag requesting the CFDData objects themselves.
        The default is False.
    """

    if fetch_data:
        return [pd for pd in CFDType._path_types.values()]
    else:
        return [key.lower() for key in CFDType._path_types.keys()]


def merge_json(path: str) -> None:
    """
    Takes an external JSON dialog data file and merges its contents to the
    package's own file. This way if you create dialogs you can reuse them in
    another project.

    :param path: Path to the external JSON dialog data file.
    """

    with open(cfd_data_file_path(), 'r') as f:
        package_data = json.load(f)

    package_data = [CFDData.from_dict(pdo) for pdo in package_data]

    with open(path, 'r') as f:
        external_data = json.load(f)

    external_data = [CFDData.from_dict(pdo) for pdo in external_data]

    pd_len = len(package_data)  # len used to not have to check newly...
    for pdo_e in external_data:  # ... appended items
        if all(not pdo_e.soft_eq(pdo_p) for pdo_p in package_data[:pd_len]):
            package_data.append(pdo_e)

    package_data = [pdo.as_dict for pdo in package_data]

    with open(cfd_data_file_path(), 'w') as f:
        json.dump(package_data, f, indent=4)

    if not any('pytest' in arg for arg in sys.argv):  # Disable during test
        try:
            os.remove(os.path.join(_PACKAGE_DIR, 'custom_file_dialog.pyi'))
        except FileNotFoundError:
            pass
        else:
            _init_module()  # Reinitialize the module so that types are reloaded


@dataclass
class CFDData:
    """ Data describing a configuration for a given custom file dialog (CFD).

    :param path_id: Unique text identifier of the path.
    :param window_title: Title to set for the dialog.
    :param dialog_type: Numeric identifier for open/save file or open directory.
    :param file_type_filter: String filter for file handler dialogs
        (e.g. "JSON (*.json)").
    :param path: Absolute path to start browsing from.
    """

    path_id: str
    window_title: str
    dialog_type: int
    file_type_filter: str = ''
    path: str = 'C:/'

    def __eq__(self, other) -> bool:
        """ Custom comparison rule, comparing each field. """

        if not isinstance(other, CFDData):
            return False

        return all(getattr(self, f.name) == getattr(other, f.name)
                   for f in fields(self))

    def soft_eq(self, other) -> bool:
        """ Custom soft comparison rule, comparing only the ID. """

        if not isinstance(other, CFDData):
            return False

        return self.path_id == other.path_id  # type: ignore

    @property
    def as_dict(self) -> dict:
        """ Returns a dictionary containing the set values. """

        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, src: dict) -> CFDData:
        """ Returns an instance built from a dictionary.

        :param src: A dictionary containing data to build an instance,
            extracted from the handled JSON file.
        """

        return cls(**src)


def _import_json(full_id_key: bool = False) -> dict[str, CFDData] | None:
    """ Imports data from the handled JSON file.

    :param full_id_key: A flag marking whether to keep the full ID as key
        or to format it (default) beforehand.

    :returns: A dictionary with keys of path IDs and values of CFDData objects,
        imported from the handled JSON file (or None if there is no such file).
    """

    try:
        with open(cfd_data_file_path(), 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return
    else:
        types_dict = {}
        for path_item in data:
            if full_id_key:
                key = path_item['path_id']
            else:
                path_type = path_item['path_id'][0]
                key = (path_item['path_id'].split('_', 1)[1]
                       .capitalize().replace('_', ' '))
                key = f"[{path_type}] {key}"

            types_dict[key] = CFDData(**path_item)

        return types_dict


class _FileDialogDataEditor(QDialog):
    """ An editor for developer use. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        super().__init__(parent=None)

        self.setWindowTitle("File dialog data editor")
        self.setFixedWidth(400)

        self._file_dialog_types = _import_json()

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkNewType = QCheckBox(text="New type", parent=None)
        self._cmbTypeList = QComboBox()
        self._cmbPathCategory = QComboBox()
        self._cmbPathCategory.addItems(['Source', 'Destination'])
        self._ledPathType = QLineEdit()
        self._ledPathType.setPlaceholderText("Path type")
        self._ledWindowTitle = QLineEdit()
        self._ledWindowTitle.setPlaceholderText("Window title")
        self._cmbDialogTypes = QComboBox()
        self._cmbDialogTypes.addItems(["Open file name",
                                       "Save file name",
                                       "Existing directory"])
        self._ledFileTypeFilter = QLineEdit()
        self._ledFileTypeFilter.setPlaceholderText("CSV (*.csv)")
        self._ledPath = QLineEdit()
        self._ledPath.setPlaceholderText('Path')
        self._btnDelete = QPushButton('Delete')
        self._btnExport = QPushButton('Export')

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._chkNewType)
        self._vloMainLayout.addWidget(self._cmbTypeList)
        self._vloMainLayout.addWidget(self._cmbPathCategory)
        self._vloMainLayout.addWidget(self._ledPathType)
        self._vloMainLayout.addWidget(self._ledWindowTitle)
        self._vloMainLayout.addWidget(self._cmbDialogTypes)
        self._vloMainLayout.addWidget(self._ledFileTypeFilter)
        self._vloMainLayout.addWidget(self._ledPath)
        self._vloMainLayout.addWidget(self._btnDelete)
        self._vloMainLayout.addWidget(self._btnExport)

        self.setLayout(self._vloMainLayout)

        # Further initialization
        if self._file_dialog_types is None:
            self._chkNewType.setChecked(True)
            self._cmbTypeList.setVisible(False)
        else:
            self._update_type_list_combobox()
            self._slot_type_selection_changed()

        self._slot_new_type_toggled()

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._chkNewType.stateChanged, self._slot_new_type_toggled)
        qt_connect(self._cmbTypeList.currentIndexChanged,
                   self._slot_type_selection_changed)
        qt_connect(self._btnDelete.clicked, self._slot_delete_data)
        qt_connect(self._btnExport.clicked, self._slot_export_data)

    def _export_json(self) -> None:
        """ Exports data to the handled JSON file. """

        if self._file_dialog_types is None:
            os.remove(cfd_data_file_path())
            return

        with open(cfd_data_file_path(), 'w') as f:
            json.dump([t.as_dict for t in self._file_dialog_types.values()],
                      f, indent=4)

    def _reset_inputs(self) -> None:
        """ Resets the input fields to their default values. """

        self._cmbPathCategory.setCurrentIndex(0)
        self._ledPathType.setText('')
        self._ledWindowTitle.setText('')
        self._cmbDialogTypes.setCurrentIndex(0)
        self._ledFileTypeFilter.setText('')
        self._ledPath.setText('')

    def _slot_new_type_toggled(self) -> None:
        """
        Sets the visibility of the type selector based on the control combobox.
        """

        self._cmbTypeList.setVisible(not self._chkNewType.isChecked())
        if not self._chkNewType.isChecked():  # Update by the currently...
            self._slot_type_selection_changed()  # ...selected existing theme

    def _slot_type_selection_changed(self) -> None:  # Index unused: not a param
        """ Updates the GUI according to the control combobox. """

        path_data: CFDData = self._file_dialog_types[
            self._cmbTypeList.currentText()]
        self._cmbPathCategory.setCurrentIndex(path_data.path_id.startswith('D'))
        self._ledPathType.setText(self._cmbTypeList.currentText()
                                  .split(' ', 1)[1])
        self._ledWindowTitle.setText(path_data.window_title)
        self._cmbDialogTypes.setCurrentIndex(path_data.dialog_type)
        self._ledFileTypeFilter.setText(path_data.file_type_filter)
        self._ledPath.setText(path_data.path)

    def _update_type_list_combobox(self) -> None:
        """ Updates the combobox from the type list. """

        with SignalBlocker(self._cmbTypeList) as obj:
            obj.clear()
            if self._file_dialog_types is not None:
                obj.addItems(self._file_dialog_types.keys())  # type: ignore
                obj.setCurrentIndex(obj.count() - 1)

    def _slot_delete_data(self) -> None:
        """ Attempts to delete the set data, updating the GUI. """

        pt = self._ledPathType.text()
        pt = f"[{self._cmbPathCategory.currentText()[0]}] {pt}"
        try:
            del self._file_dialog_types[pt]
        except (TypeError, KeyError):  # TypeError if None
            return
        else:
            if not self._file_dialog_types:  # Empty list
                self._file_dialog_types = None

            self._export_json()
            self._update_type_list_combobox()
            if self._file_dialog_types is not None:
                self._slot_type_selection_changed()
            else:
                self._chkNewType.setChecked(True)
                self._reset_inputs()

    def _slot_export_data(self) -> None:
        """
        Adds the set data to the stored dictionary and exports it, updating
        the GUI.
        """

        pc = self._cmbPathCategory.currentText().upper()
        pt = self._ledPathType.text()
        path_data = CFDData(f"{pc}_{pt.upper().replace(' ', '_')}",
                            self._ledWindowTitle.text(),
                            self._cmbDialogTypes.currentIndex(),
                            self._ledFileTypeFilter.text(),
                            self._ledPath.text())

        pt = f"[{self._cmbPathCategory.currentText()[0]}] {pt}"
        try:
            self._file_dialog_types[pt] = path_data
        except TypeError:  # If None
            self._file_dialog_types = {pt: path_data}

        self._export_json()
        self._update_type_list_combobox()
        self._chkNewType.setChecked(False)


class _CFDType(metaclass=Singleton):
    """ A class for Enum-like access to custom file dialog (CFD) types. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        self._path_types = _import_json(full_id_key=True)

    def __getattr__(self, name: str) -> CFDData | None:
        """
        Returns the CFDData object identified by the passed string if there are
        CFD types loaded.

        :param name: The unique identifier of a path.
        """

        if self._path_types is not None:
            return self._path_types[name.upper()]


def custom_dialog(parent: QWidget, cfd_data: CFDData,
                  custom_title: str = None) -> tuple[bool, str | None]:
    """ Opens a file dialog of the requested type.

    :param parent: The widget from which the dialog is requested.
    :param cfd_data: An object defining the appearance and path of the dialog.
    :param custom_title: A custom title for the dialog. The default is None,
        which means that the one defined in the 'path_data' is used.

    :returns: A tuple containing the success flag and the selected path or None
        if the selection is unsuccessful.
    """

    selection_successful = False
    if custom_title is None:
        window_title = cfd_data.window_title
    else:
        window_title = custom_title

    path = ''
    if (dialog_type := cfd_data.dialog_type) == 0:  # Open file name
        path = QFileDialog.getOpenFileName(parent,  # type: ignore
                                           window_title,
                                           cfd_data.path,
                                           cfd_data.file_type_filter)
    elif dialog_type == 1:  # Save file name
        path = QFileDialog.getSaveFileName(parent,  # type: ignore
                                           window_title,
                                           cfd_data.path,
                                           cfd_data.file_type_filter)
    elif dialog_type == 2:  # Existing directory
        path = QFileDialog.getExistingDirectory(parent,  # type: ignore
                                                window_title,
                                                cfd_data.path)

    if dialog_type <= 1:
        selection_successful = path[0] != ''
        path = path[0]
    elif dialog_type == 2:
        selection_successful = path != ''

    if not selection_successful:
        return False, None

    new_path = ''
    if dialog_type <= 1:
        path_split = path.split('/')
        for i in range(len(path_split) - 1):
            new_path += path_split[i] + '/'
    elif dialog_type == 2:
        new_path = path

    with open(cfd_data_file_path(), 'r+') as f:
        data = json.load(f)
        for idx, entry in enumerate(data):
            if entry['path_id'] == cfd_data.path_id:
                data[idx]['path'] = new_path
                break

        f.seek(0)  # Jump to the beginning of the file
        json.dump(data, f, indent=4)

    return True, path


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
        self._btnDataEditor = QPushButton("Open a data editor dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnDataEditor)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._btnDataEditor.clicked, self._slot_de_test)

    @classmethod
    def _slot_de_test(cls) -> None:
        """ Tests the data editor dialog. """

        de = _FileDialogDataEditor()
        de.exec()


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
                 in get_functions(__file__, ignores=['_import_json',
                                                     '_init_module'])]

    reprs = [stub_repr(func) for func in functions]
    reprs.append('\n\n')

    class_reprs = []
    classes = {globals().get(cls_name): signals
               for cls_name, signals in get_classes(__file__).items()}

    for cls, sigs in classes.items():
        if cls == _CFDType:
            try:
                with open(cfd_data_file_path(), 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                extra_cvs = None
            else:
                extra_cvs = '\n'.join([f"\t{path_item['path_id'].lower()}: "
                                       "CFDData = None"
                                       for path_item in data])
        else:
            extra_cvs = None

        class_reprs.append(
            stub_repr(cls, signals=sigs, extra_cvs=extra_cvs))

    reprs.append('\n\n'.join(class_reprs))

    with open(stub_path, 'w') as f:
        f.write(imports)
        f.write("CFDType: _CFDType = None\n\n\n")
        f.write(''.join(reprs))


def _init_module():
    """ Initializes the module. """

    write_stub()

    global CFDType
    CFDType = _CFDType()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
