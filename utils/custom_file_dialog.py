""" File dialogs customized by a JSON file. """

from __future__ import annotations

__author__ = "Mihaly Konda"
__version__ = '1.0.0'


# Built-in modules
import os
from dataclasses import dataclass, fields
import json
import sys

# Qt6 modules
from PySide6.QtWidgets import *

# Custom modules
from utils._general import SignalBlocker


PathTypes: _PathTypes | None = None


@dataclass
class PathData:
    """ Data describing a configuration for a given path. """

    path_id: str
    window_title: str
    dialog_type: int
    file_type_filter: str = ''
    path: str = 'C:/'

    @property
    def as_dict(self) -> dict:
        """ Returns a dictionary containing the set values. """

        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def _stub_repr(cls) -> str:
        """ Helper class method for stub file creation. """

        repr_ = f"class {cls.__name__}:\n"
        repr_ += "\tpath_id = None  # type: str\n"
        repr_ += "\twindow_title = None  # type: str\n"
        repr_ += "\tdialog_type = None  # type: int\n"
        repr_ += "\tfile_type_filter = None  # type: str\n"
        repr_ += "\tpath = None  # type: str\n\n"

        return repr_


def _import_json(full_id_key=False) -> dict[str, PathData] | None:
    """ Imports data from the handled JSON file.

    Parameters
    ----------
    full_id_key: bool, optional
        A flag marking whether to keep the full ID as key or to
        format it (default) beforehand.
    """

    try:
        with open('./custom_file_dialog_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return
    else:
        types_dict = {}
        for path_item in data:
            if full_id_key:
                key = path_item['path_id']
            else:
                key = (path_item['path_id'].split('_', 1)[1]
                       .capitalize().replace('_', ' '))

            types_dict[key] = PathData(**path_item)

        return types_dict


class _FileDialogDataEditor(QDialog):
    """ An editor for developer use. """

    def __init__(self):
        """ Initializer for the class. """

        super().__init__()

        self.setWindowTitle("File dialog data editor")
        self.setFixedWidth(400)

        self._file_dialog_types = _import_json()

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkNewType = QCheckBox("New type")
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
            self._cmbTypeList.addItems(self._file_dialog_types.keys())
            self._slot_type_selection_changed()

        self._slot_new_type_toggled()

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._chkNewType.stateChanged.connect(self._slot_new_type_toggled)
        self._cmbTypeList.currentIndexChanged.connect(
            self._slot_type_selection_changed)
        self._btnDelete.clicked.connect(self._slot_delete_data)
        self._btnExport.clicked.connect(self._slot_export_data)

    def _export_json(self) -> None:
        """ Exports data to the handled JSON file. """

        if self._file_dialog_types is None:
            os.remove('./custom_file_dialog_data.json')
            return

        with open('./custom_file_dialog_data.json', 'w') as f:
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
        """ Sets the visibility of the type selector based on
        the control combobox. """

        self._cmbTypeList.setVisible(not self._chkNewType.isChecked())
        if not self._chkNewType.isChecked():  # Update by the currently...
            self._slot_type_selection_changed()  # ...selected existing theme

    def _slot_type_selection_changed(self) -> None:  # Index unused: not a param
        """ Updates the GUI according to the control combobox. """

        path_data: PathData = self._file_dialog_types[
            self._cmbTypeList.currentText()]
        self._cmbPathCategory.setCurrentIndex(path_data.path_id.startswith('D'))
        self._ledPathType.setText(self._cmbTypeList.currentText())
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

        try:
            del self._file_dialog_types[self._ledPathType.text()]
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
        """ Adds the set data to the stored dictionary and
        exports it, updating the GUI. """

        pc = self._cmbPathCategory.currentText().upper()
        pt = self._ledPathType.text()
        path_data = PathData(f"{pc}_{pt.upper().replace(' ', '_')}",
                             self._ledWindowTitle.text(),
                             self._cmbDialogTypes.currentIndex(),
                             self._ledFileTypeFilter.text(),
                             self._ledPath.text())

        try:
            self._file_dialog_types[pt] = path_data
        except TypeError:  # If None
            self._file_dialog_types = {pt: path_data}

        self._export_json()
        self._update_type_list_combobox()
        self._chkNewType.setChecked(False)


class _PathTypes:
    """ A collection of the defined path types. """

    def __init__(self):
        self._path_types = _import_json(full_id_key=True)

    def __getattr__(self, name):
        if self._path_types is not None:
            return self._path_types[name.upper()]

    @classmethod
    def _stub_repr(cls) -> str:
        """ Helper class method for stub file creation. """

        repr_ = f"class {cls.__name__}:\n"
        if (path_types := _import_json()) is None:
            repr_ += '\t...\n\n'
            return repr_

        repr_ += '\n'.join([f"\t{pd.path_id.lower()} = None  # type: PathData"
                            for pd in path_types.values()])

        return repr_


def custom_dialog(parent, path_data, custom_title=None)\
        -> tuple[bool, str | None]:
    """ Opens a file dialog of the requested type.

    Parameters
    ----------
    parent : QWidget
        The widget from which the dialog is requested.

    path_data : PathData
        An object defining the appearance and path of the dialog.

    custom_title : str, optional
        A custom title for the dialog. The default is None, which
        means that the one defined in the 'path_data' is used.
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

        with open('custom_file_dialog_data.json', 'r+') as f:
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
        self._btnDataEditor = QPushButton("Open a data editor dialog")

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnDataEditor)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnDataEditor.clicked.connect(self._slot_de_test)

    @staticmethod
    def _slot_de_test() -> None:
        """ Tests the data editor dialog. """

        de = _FileDialogDataEditor()
        de.exec()


def _init_module():
    """ Initializes the module. """

    if not os.path.exists('custom_file_dialog.pyi'):
        with open('custom_file_dialog.pyi', 'w') as f:
            f.write("PathTypes = None  # type: _PathTypes\n\n")
            f.write(PathData._stub_repr())
            f.write(_PathTypes._stub_repr())
            f.write('\n\n')
            f.write("def custom_dialog(parent, path_data, custom_title=None)")
            f.write(" -> tuple[bool, str | None]: ...")

    global PathTypes
    if PathTypes is None:
        PathTypes = _PathTypes()


_init_module()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
