""" File dialogs customized by a JSON file. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.0.6'


# Built-in modules
import os
from dataclasses import dataclass, fields
import json
import sys

# Qt6 modules
from PySide6.QtWidgets import *

# Custom modules
from utils_qt_mk import _PACKAGE_DIR
from utils_qt_mk._general import SignalBlocker, Singleton, stub_repr


PathTypes: _PathTypes | None = None


def get_path_types(fetch_data: bool = False) -> list[str | PathData]:
    """ Returns the available path types.

    :param fetch_data: A flag requesting the PathData objects themselves.
        The default is False.
    """

    if fetch_data:
        return [pd for pd in PathTypes._path_types.values()]
    else:
        return [key.lower() for key in PathTypes._path_types.keys()]


def merge_json(path: str) -> None:
    """
    Takes an external JSON dialog data file and merges its contents to the
    package's own file. This way if you create dialogs you can reuse them in
    another project.

    :param path: Path to the external JSON dialog data file.
    """

    with open(os.path.join(_PACKAGE_DIR, 'custom_file_dialog_data.json'),
              'r') as f:
        package_data = json.load(f)

    package_data = [PathData.from_dict(pdo) for pdo in package_data]

    with open(path, 'r') as f:
        external_data = json.load(f)

    external_data = [PathData.from_dict(pdo) for pdo in external_data]

    pd_len = len(package_data)
    for pdo_e in external_data:  # len used to not have to check newly appended
        if all(pdo_e != pdo_p for pdo_p in package_data[:pd_len]):  # items
            package_data.append(pdo_e)

    package_data = [pdo.as_dict for pdo in package_data]

    with open(os.path.join(_PACKAGE_DIR, 'custom_file_dialog_data.json'),
              'w') as f:
        json.dump(package_data, f, indent=4)

    try:
        os.remove(os.path.join(_PACKAGE_DIR, 'custom_file_dialog.pyi'))
    except FileNotFoundError:
        pass
    else:
        _init_module()  # Reinitialize the module so that types are reloaded


@dataclass
class PathData:
    """ Data describing a configuration for a given path.

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

        if not isinstance(other, PathData):
            return False

        return all(getattr(self, f.name) == getattr(other, f.name)
                   for f in fields(self))

    @property
    def as_dict(self) -> dict:
        """ Returns a dictionary containing the set values. """

        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, src: dict) -> PathData:
        """ Returns an instance built from a dictionary.

        :param src: A dictionary containing data to build an instance,
            extracted from the handled JSON file.
        """

        return cls(**src)


def _import_json(full_id_key: bool = False) -> dict[str, PathData] | None:
    """ Imports data from the handled JSON file.

    :param full_id_key: A flag marking whether to keep the full ID as key
        or to format it (default) beforehand.

    :returns: A dictionary with keys of path IDs and values of PathData objects,
        imported from the handled JSON file (or None if there is no such file).
    """

    try:
        with open(os.path.join(_PACKAGE_DIR, 'custom_file_dialog_data.json'),
                  'r') as f:
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

            types_dict[key] = PathData(**path_item)

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
        self._cmbTypeList = QComboBox()  # type: ignore
        self._cmbPathCategory = QComboBox()  # type: ignore
        self._cmbPathCategory.addItems(['Source', 'Destination'])
        self._ledPathType = QLineEdit()  # type: ignore
        self._ledPathType.setPlaceholderText("Path type")
        self._ledWindowTitle = QLineEdit()  # type: ignore
        self._ledWindowTitle.setPlaceholderText("Window title")
        self._cmbDialogTypes = QComboBox()  # type: ignore
        self._cmbDialogTypes.addItems(["Open file name",
                                       "Save file name",
                                       "Existing directory"])
        self._ledFileTypeFilter = QLineEdit()  # type: ignore
        self._ledFileTypeFilter.setPlaceholderText("CSV (*.csv)")
        self._ledPath = QLineEdit()  # type: ignore
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

        self._chkNewType.stateChanged.connect(  # type: ignore
            self._slot_new_type_toggled)
        self._cmbTypeList.currentIndexChanged.connect(  # type: ignore
            self._slot_type_selection_changed)
        self._btnDelete.clicked.connect(self._slot_delete_data)  # type: ignore
        self._btnExport.clicked.connect(self._slot_export_data)  # type: ignore

    def _export_json(self) -> None:
        """ Exports data to the handled JSON file. """

        if self._file_dialog_types is None:
            os.remove(os.path.join(_PACKAGE_DIR,
                                   'custom_file_dialog_data.json'))
            return

        with open(os.path.join(_PACKAGE_DIR,
                               'custom_file_dialog_data.json'), 'w') as f:
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
        Sets the visibility of the type selector based on
        the control combobox.
        """

        self._cmbTypeList.setVisible(not self._chkNewType.isChecked())
        if not self._chkNewType.isChecked():  # Update by the currently...
            self._slot_type_selection_changed()  # ...selected existing theme

    def _slot_type_selection_changed(self) -> None:  # Index unused: not a param
        """ Updates the GUI according to the control combobox. """

        path_data: PathData = self._file_dialog_types[
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
                obj.addItems(self._file_dialog_types.keys())
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
        path_data = PathData(f"{pc}_{pt.upper().replace(' ', '_')}",
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


class _PathTypes(metaclass=Singleton):
    """ A src of the defined path types. """

    def __init__(self) -> None:
        """ Initializer for the class. """

        self._path_types = _import_json(full_id_key=True)

    def __getattr__(self, name: str) -> PathData | None:
        """
        Returns PathData identified by the passed string if there are path
        types loaded.

        :param name: The unique identifier of a path.
        """

        if self._path_types is not None:
            return self._path_types[name.upper()]


def custom_dialog(parent: QWidget, path_data: PathData,
                  custom_title: str = None) -> tuple[bool, str | None]:
    """ Opens a file dialog of the requested type.

    :param parent: The widget from which the dialog is requested.
    :param path_data: An object defining the appearance and path of the dialog.
    :param custom_title: A custom title for the dialog. The default is None,
        which means that the one defined in the 'path_data' is used.

    :returns: A tuple containing the success flag and the selected path or None
        if the selection is unsuccessful.
    """

    selection_successful = False
    if custom_title is None:
        window_title = path_data.window_title
    else:
        window_title = custom_title

    if (dialog_type := path_data.dialog_type) == 0:  # Open file name
        path = QFileDialog.getOpenFileName(parent,
                                           window_title,
                                           path_data.path,
                                           path_data.file_type_filter)
    elif dialog_type == 1:  # Save file name
        path = QFileDialog.getSaveFileName(parent,
                                           window_title,
                                           path_data.path,
                                           path_data.file_type_filter)
    elif dialog_type == 2:  # Existing directory
        path = QFileDialog.getExistingDirectory(parent,
                                                window_title,
                                                path_data.path)

    if dialog_type <= 1:
        selection_successful = path[0] != ''
        path = path[0]
    elif dialog_type == 2:
        selection_successful = path != ''

    if selection_successful:
        if dialog_type <= 1:
            path_split = path.split('/')
            new_path = ''
            for i in range(len(path_split) - 1):
                new_path += path_split[i] + '/'
        elif dialog_type == 2:
            new_path = path

        with open(os.path.join(_PACKAGE_DIR, 'custom_file_dialog_data.json'),
                  'r+') as f:
            data = json.load(f)
            for idx, entry in enumerate(data):
                if entry['path_id'] == path_data.path_id:
                    data[idx]['path'] = new_path
                    break

            f.seek(0)  # Jump to the beginning of the file
            json.dump(data, f, indent=4)

        return True, path
    else:
        return False, None


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

        self._wdgCentralWidget = QWidget()  # type: ignore
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnDataEditor.clicked.connect(self._slot_de_test)  # type: ignore

    @classmethod
    def _slot_de_test(cls) -> None:
        """ Tests the data editor dialog. """

        de = _FileDialogDataEditor()
        de.exec()


def _init_module():
    """ Initializes the module. """

    if not os.path.exists(os.path.join(_PACKAGE_DIR, 'custom_file_dialog.pyi')):
        imports = "from dataclasses import dataclass\n" \
                  "from PySide6.QtWidgets import QDialog, QMainWindow, " \
                  "QWidget\n" \
                  "from utils_qt_mk._general import Singleton\n\n\n"

        functions = [get_path_types, merge_json, _import_json, custom_dialog]
        reprs = [stub_repr(func) for func in functions]
        reprs.append('\n\n')

        classes = {PathData: None,
                   _FileDialogDataEditor: None,
                   _PathTypes: None,
                   _TestApplication: None}

        class_reprs = []
        for cls, sigs in classes.items():
            if cls == _PathTypes:
                try:
                    with open(os.path.join(_PACKAGE_DIR,
                                           'custom_file_dialog_data.json'),
                              'r') as f:
                        data = json.load(f)
                except FileNotFoundError:
                    extra_cvs = None
                else:
                    extra_cvs = '\n'.join([f"\t{path_item['path_id'].lower()}: "
                                           "PathData = None"
                                           for path_item in data])
            else:
                extra_cvs = None

            class_reprs.append(
                stub_repr(cls, signals=sigs, extra_cvs=extra_cvs))

        reprs.append('\n\n'.join(class_reprs))

        with open(os.path.join(_PACKAGE_DIR, 'custom_file_dialog.pyi'),
                  'w') as f:
            f.write(imports)
            f.write("PathTypes: _PathTypes = None\n\n\n")
            f.write(''.join(reprs))

    global PathTypes
    PathTypes = _PathTypes()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
