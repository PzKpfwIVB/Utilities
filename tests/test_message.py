""" Test cases for the message module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
import json
import os

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.config import set_mbt_file_path, mbt_file_path
set_mbt_file_path(os.path.join(os.path.split(__file__)[0],
                               'messagebox_types.json'))

from utils_qt_mk.message import *
from utils_qt_mk.message import _MessageBoxData  # type: ignore


test_dict = {'icon': 2, 'title': 'WARNING', 'text': "This is a warning!",
             'buttons': [1024, 16_777_216], 'flags': [9, 3]}


def test_get_messagebox_types() -> None:
    mbt = get_messagebox_types(fetch_data=True)
    assert mbt == [_MessageBoxData(icon=QMessageBox.Icon.Question,
                                   title='Quit',
                                   text="Are you sure you want to quit?",
                                   buttons=[QMessageBox.StandardButton.Yes,
                                            QMessageBox.StandardButton.No],
                                   flags=[Qt.WindowType
                                          .MSWindowsFixedSizeDialogHint])]

    mbt_str = get_messagebox_types()
    assert mbt_str == ['close_event_question']


def test__MessageBoxData() -> None:
    # Buttons: 0x00000400 | 0x01000000 = 0x01000400 = 16 778 240
    # Flags: 0x00000009 | 0x00000003 = 0x0000000B = 11
    mbd = _MessageBoxData(icon=QMessageBox.Icon.Warning,
                          title='WARNING',
                          text="This is a warning!",
                          buttons=[QMessageBox.StandardButton.Ok,
                                   QMessageBox.StandardButton.Help],
                          flags=[Qt.WindowType.Popup, Qt.WindowType.Dialog])

    assert mbd.icon == QMessageBox.Icon.Warning
    assert mbd.title == 'WARNING'
    assert mbd.text == "This is a warning!"
    assert (mbd.merged_bits(attr='buttons') == QMessageBox
            .StandardButton(16_778_240))
    assert mbd.merged_bits(attr='flags') == Qt.WindowType(11)

    assert mbd.as_dict == test_dict
    mbd_copy = _MessageBoxData.from_dict(test_dict)
    assert mbd_copy == mbd


def test__MessageBoxType() -> None:
    mbd_copy = _MessageBoxData.from_dict(test_dict)
    MessageBoxType['test_warning'] = mbd_copy  # type: ignore
    assert MessageBoxType.test_warning == mbd_copy  # type: ignore

    MessageBoxType.export_types()
    with open(mbt_file_path(), 'r') as file:
        modified_content = json.load(file)  # Test MBT exported

    assert modified_content[1] == {'type_id': 'test_warning'} | test_dict
    assert MessageBoxType.is_empty() is False
    assert MessageBoxType.converted_keys() == ['Close event question',
                                               'Test warning']

    del MessageBoxType['test_warning']  # type: ignore

    MessageBoxType.export_types()
    with open(mbt_file_path(), 'r') as file:
        modified_content = json.load(file)  # Test MBT deleted

    assert len(modified_content) == 1
