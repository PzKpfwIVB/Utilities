""" A module for a mix of custom widgets. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'


# Built-in modules
from collections.abc import Iterator
from typing import TypeVar


# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Custom modules
from utils_qt_mk.general import SignalBlocker, qt_connect


CustomWidgetT = TypeVar('CustomWidgetT', bound=QWidget)


class WheelEventFilter(QObject):
    """
    Event filter for blocking wheel events, install it on a target widget.
    The constructor needs a parent so the filter won't get garbage-collected.
    Needed as focusPolicy is ignored in PySide6 v6.6.2
    """

    def eventFilter(self, watched: CustomWidgetT, event: QEvent) -> bool:
        """ Overridden event filter method.

        :param watched: The watched object.
        :param event: The caught event.
        """

        if event.type() == QEvent.Type.Wheel:
            watched.clearFocus()
            return True  # Event is marked as handled

        return super().eventFilter(watched, event)


class WidgetListWidget(QWidget):
    """ A widget that emulates a QListWidget for QWidgets.

    .. note:: Each contained widget is expected to inherit ListMixin.
    """

    def __init__(self, widgets: list = None) -> None:
        """ Initializer for the class.

        :param widgets: The list of widgets to add to the list.
        """

        super().__init__(parent=None)

        self._widgets = widgets if widgets is not None else []
        self._update_widget_names()

        self._setup_ui()
        self._setup_connections()
        self._visual_update()

    def __getitem__(self, index: int) -> CustomWidgetT:
        """ Returns the widget from the requested index in the list.

        :param index: The index of the widget to return.
        """

        return self._widgets[index]

    def __iter__(self) -> Iterator[CustomWidgetT]:
        """ Makes the object iterable, yielding the widgets of the list. """

        for wdg in self._widgets:
            yield wdg

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._scrollWidget = QWidget()  # type: ignore
        self._verticalScrollArea = QScrollArea()  # type: ignore
        self._verticalScrollArea.setWidgetResizable(True)

        # Layouts
        self._vloScrollLayout = QVBoxLayout()
        self._scrollWidget.setLayout(self._vloScrollLayout)
        self._verticalScrollArea.setWidget(self._scrollWidget)

        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._verticalScrollArea)
        self._vloMainLayout.setSpacing(0)
        self._vloMainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._vloMainLayout)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        for wdg in self._widgets:
            wdg.selected.connect(self._update_selection,
                                 type=Qt.ConnectionType.UniqueConnection)

    @property
    def widget_count(self) -> int:
        """ Returns the number of widgets in the list. """

        return len(self._widgets)

    @property
    def selection(self) -> int:
        """ Returns the selection index or -1 if no widget is selected. """

        for wdg in self._widgets:
            if wdg.is_selected:
                return int(wdg.objectName())

        return -1

    def _update_widget_names(self) -> None:
        """ Updates the widgets' objectName by their position in the list. """

        for idx, wdg in enumerate(self._widgets):
            wdg.setObjectName(str(idx))

    def list_handler(self, command: str, widget: CustomWidgetT = None) -> bool:
        """ Handles list operations (e.g. adding a widget to the list).

        :param command: 'a', 'r', 'u', 'd' for adding, removing, moving up or
            down a widget, respectively. To clear the list, use 'c'.
        :param widget: Optional parameter, the widget to be added to the list.

        :returns: A success flag.
        """

        if command == 'a':
            self._widgets.append(widget)
        elif command == 'r':
            if (s := self.selection) >= 0:
                self._widgets.pop(s)
            else:
                return False
        elif command == 'u':
            if (s := self.selection) > 0:  # The item at idx 0 can't be moved up
                self._widgets[s - 1], self._widgets[s] = (self._widgets[s],
                                                          self._widgets[s - 1])
            else:
                return False
        elif command == 'd':
            if -1 < (s := self.selection) < len(self._widgets) - 1:
                self._widgets[s], self._widgets[s + 1] = (self._widgets[s + 1],
                                                          self._widgets[s])
            else:
                return False
        elif command == 'c':
            self._widgets = []
        else:
            return False  # Unknown command

        self._update_widget_names()
        self._setup_connections()
        self._visual_update()

        return True

    def _update_selection(self) -> None:
        """ Emulates the selection behaviour of a button group. """

        sender_id = int(self.sender().objectName())
        for idx, wdg in enumerate(self._widgets):
            if idx != sender_id:
                wdg.deselect()

    def _visual_update(self) -> None:
        """ Provides visual update to the list widget. """

        self._scrollWidget = QWidget()  # type: ignore
        self._vloScrollLayout = QVBoxLayout()
        for wdg in self._widgets:
            self._vloScrollLayout.addWidget(wdg)

        self._vloScrollLayout.addStretch(0)

        self._scrollWidget.setLayout(self._vloScrollLayout)
        self._verticalScrollArea.setWidget(self._scrollWidget)


class ListMixin:
    """
    Mixin class to make a QWidget compatible with the WidgetListWidget.

    Expects the target widget to use the checkbox named `_chkSelection` (created
    here).

    **Note:** remember to call `_setup_ui()` and `_setup_connections()` with
    `super()` in the subclass.

    :cvar selected: A signal indicating that the widget got selected.
    """

    selected = Signal()

    def __init__(self) -> None:
        """ Initializer for the class. """

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._chkSelection = QCheckBox()  # type: ignore

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._chkSelection.stateChanged, self._slot_selected)

    def _slot_selected(self) -> None:
        """ Emits the selection signal. """

        self.selected.emit()

    @property
    def is_selected(self) -> bool:
        """ Returns the selection state of the selection checkbox. """

        return self._chkSelection.isChecked()

    def deselect(self) -> None:
        """ Deselects the widgets while blocking the corresponding signal. """

        with SignalBlocker(self._chkSelection) as obj:
            obj.setChecked(False)
