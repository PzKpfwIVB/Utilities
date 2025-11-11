""" Test cases for the widget_mix module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.widget_mix import *


class TestListWidget(QWidget, ListMixin):
    """ Widget for testing the ListMixin class. """

    def __init__(self, wdg_id: str) -> None:
        """ Initializer for the class. """

        super().__init__()

        self._setup_ui()
        self.id = wdg_id

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkSelection = QCheckBox()
        self._lblIdentifier = QLabel()

        # Layouts
        self._hloMainLayout = QHBoxLayout()
        self._hloMainLayout.addWidget(self._chkSelection)
        self._hloMainLayout.addWidget(self._lblIdentifier)

        self.setLayout(self._hloMainLayout)

    @property
    def id(self) -> str:
        """ Returns the string identifier of the widget. """

        return self._lblIdentifier.text()

    @id.setter
    def id(self, new_id: str) -> None:
        """ Sets the string identifier of the widget.

        :param new_id: The string identifier of the widget.
        """

        self._lblIdentifier.setText(new_id)


def test_WLW_and_ListMixin() -> None:
    wlw = WidgetListWidget()
    ref_wdg_list = [f'list_widget_{i}' for i in range(10)]
    for wdg_id in ref_wdg_list:
        wlw.list_handler(command='a', widget=TestListWidget(wdg_id=wdg_id))

    # [TEST] Iterability, default selection and widget lists
    assert [wdg.id for wdg in wlw] == ref_wdg_list
    assert wlw.selection == -1

    # [TEST] Simulate selection
    wlw[3]._chkSelection.setChecked(True)
    wlw[3]._slot_selected()
    assert wlw.selection == 3

    # [TEST] Move item up, check new selection index
    wlw.list_handler(command='u')
    assert wlw.selection == 2
    ref_wdg_list[2], ref_wdg_list[3] = ref_wdg_list[3], ref_wdg_list[2]
    assert [wdg.id for wdg in wlw] == ref_wdg_list

    # [TEST] Move item back down, check new selection index
    wlw.list_handler(command='d')
    assert wlw.selection == 3
    ref_wdg_list[2], ref_wdg_list[3] = ref_wdg_list[3], ref_wdg_list[2]
    assert [wdg.id for wdg in wlw] == ref_wdg_list

    # [TEST] Reselection and item removal
    wlw[7]._chkSelection.setChecked(True)
    wlw[7]._slot_selected()
    assert wlw.selection == 7
    assert wlw.list_handler(command='r') is True
    ref_wdg_list.pop(7)
    assert [wdg.id for wdg in wlw] == ref_wdg_list

    # [TEST] Clearing the list
    wlw.list_handler(command='c')
    assert wlw.widget_count == 0

    # [TEST] Remove nonexistent list item
    assert wlw.list_handler(command='r') is False
