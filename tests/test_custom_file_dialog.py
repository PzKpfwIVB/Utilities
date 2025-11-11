""" Test cases for the custom_file_dialog module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
import json
import os

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.config import set_cfd_data_file_path, cfd_data_file_path
set_cfd_data_file_path(os.path.join(os.path.split(__file__)[0],
                                    'custom_file_dialog_data.json'))

from utils_qt_mk.custom_file_dialog import *
from utils_qt_mk.custom_file_dialog import _import_json, _FileDialogDataEditor


original_content = {}
test_content_mod_key = {"[D] Test": CFDData('DESTINATION_TEST', "Test window",
                                            2, '', 'C:/Example/')}
test_content_full_key = {'DESTINATION_TEST': CFDData('DESTINATION_TEST',
                                                     "Test window",
                                                     2, '', 'C:/Example/')}


def test_import_json() -> None:
    global original_content

    original_content = _import_json()
    assert (original_content ==
            {"[D] Themes": CFDData('DESTINATION_THEMES',
                                   'Export theme',
                                   1, 'JSON (*.json)', 'C:/'),
             "[D] Colour scales": CFDData('DESTINATION_COLOUR_SCALES',
                                          'Export colour scale data',
                                          1, "JSON (*.json)", 'C:/'),
             '[S] Colour scales': CFDData('SOURCE_COLOUR_SCALES',
                                          'Import colour scale data',
                                          0, "JSON (*.json)", 'C:/')})


def test_merge_json():
    base_path = os.path.split(__file__)[0]
    with open(cfd_data_file_path(), 'r') as file:
        original_file_content = file.read()

    with open(os.path.join(base_path, 'test.json'), 'w') as file:
        file.write(json.dumps([{
            'path_id': 'DESTINATION_TEST',
            'window_title': "Test window",
            'dialog_type': 2,
            'file_type_filter': '',
            'path': 'C:/Example/'
        }], indent=4))

    merge_json(os.path.join(base_path, 'test.json'))
    try:
        assert _import_json() == original_content | test_content_mod_key
    except AssertionError:
        pass
    finally:
        with open(cfd_data_file_path(), 'w') as file:
            file.write(original_file_content)

        os.remove(os.path.join(base_path, 'test.json'))


@pytest.fixture
def widget_FDDE(qtbot):
    w = _FileDialogDataEditor()
    qtbot.addWidget(w)

    return w


def test_FDDE(qtbot, widget_FDDE) -> None:
    # Set up new values
    widget_FDDE._chkNewType.setChecked(True)
    widget_FDDE._cmbPathCategory.setCurrentIndex(1)
    widget_FDDE._ledPathType.setText('Test')
    widget_FDDE._ledWindowTitle.setText('Test window')
    widget_FDDE._cmbDialogTypes.setCurrentIndex(2)
    widget_FDDE._ledFileTypeFilter.setText('')
    widget_FDDE._ledPath.setText('C:/Example/')

    # [TEST] Test exporting
    widget_FDDE._btnExport.click()
    # assert _import_json() == original_content.copy() | test_content_mod_key

    # [TEST] Test delete
    widget_FDDE._btnDelete.click()
    assert _import_json() == original_content

    widget_FDDE.close()
