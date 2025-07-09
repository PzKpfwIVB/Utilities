""" A cancellable, optionally nested progress dialog, reporting on a compatible
process ran by a QObject-subclass on a separate thread. """

__author__ = "Mihaly Konda"
__version__ = '1.0.2'

# Built-in modules
import sys

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtWidgets import *

# Custom modules
from utils_qt_mk.config import icon_file_path, use_theme
_ICON_FILE_PATH = icon_file_path()
_USE_THEME = use_theme()

from utils_qt_mk.general import qt_connect

if _USE_THEME:
    from utils_qt_mk.theme import set_widget_theme, ThemeParameters, WidgetTheme


def icon_file_path() -> str:
    """ Returns the path for the icon file to be used in the dialogs. """

    return _ICON_FILE_PATH


def set_icon_file_path(new_path: str = '') -> None:
    """ Sets the path for the icon file to be used in the dialogs.

    :param new_path: The new path to set for the windows. The default is an
        empty string, leading to the default icon.
    """

    global _ICON_FILE_PATH
    _ICON_FILE_PATH = new_path


class _Threaded(QObject):
    """
    An example, progress dialog compatible class.
    Worker objects of simple (not nested) PDs do not need sub-signals.

    :cvar sig_new_process_unit: A signal carrying a string identifier of the
        new main process unit.
    :cvar sig_new_subprocess_unit: A signal carrying a string identifier of
        the new subprocess unit.
    :cvar sig_main_progress: A signal carrying the progress (integer percentage)
        of the main process.
    :cvar sig_sub_progress: A signal carrying the progress (integer percentage)
        of the subprocess.
    :cvar sig_finished: The signal emitted when the process finishes.
    :cvar sig_start: The signal that starts the process execution.
    :cvar sig_cancel: A signal for external cancellation of the process
        execution.
    """

    sig_new_process_unit = Signal(str)
    sig_new_subprocess_unit = Signal(str)
    sig_main_progress = Signal(int)
    sig_sub_progress = Signal(int)
    sig_finished = Signal()  # This should carry the returned value of the proc.
    sig_start = Signal()
    sig_cancel = Signal()

    def __init__(self, nested=False) -> None:
        """ Initializer for the class.

        :param nested: A flag marking whether the progress dialog should be
            nested. The default is False.
        """

        super().__init__(parent=None)

        self._nested = nested
        self._canceled = False

        self.sig_start.connect(self._process)
        self.sig_cancel.connect(self._cancel_process)

    @property
    def nested(self) -> bool:
        """ Returns whether the associated progress dialog is nested. """

        return self._nested

    @Slot()
    def _process(self) -> None:
        """
        The slot connected to the start signal.
        Emits `sig_finished` when the process finishes.
        """

        if self._nested:
            for i in range(4):
                self.sig_new_process_unit.emit(f'Outer Iteration {i+1}')
                for j in range(6):
                    self.sig_new_subprocess_unit.emit(f'Inner Iteration {j+1}')
                    self.sig_main_progress.emit((i + 1) * 25)
                    self.sig_sub_progress.emit((j + 1) * 100/6)
                    QThread.msleep(1000)  # type: ignore
                    QCoreApplication.processEvents()  # type: ignore
                    if self._canceled:  # ^^^ To catch cancellation
                        break

                if self._canceled:
                    break
        else:
            for i in range(4):
                self.sig_new_process_unit.emit(f'Iteration {i+1}')
                self.sig_main_progress.emit((i + 1) * 25)
                QThread.msleep(1000)  # type: ignore
                QCoreApplication.processEvents()  # type: ignore
                if self._canceled:  # ^^^ To catch cancellation
                    break

        self.sig_finished.emit()

    @Slot()
    def _cancel_process(self) -> None:
        """
        The slot connected to the cancel signal.
        Needs the button press event to be processed beforehand.
        """

        self._canceled = True


class _ProgressMixin:
    """
    A window reporting on the progress of a process running on a separate
    thread.
    """

    def __init__(self, worker, title, widget_theme=None) -> None:
        """ Initializer for the class.

        :param worker: A worker subclassing QObject, handling a process.
        :param title: The title to set for the window.
        :param widget_theme: A widget theme from the 'theme' module. The default
            is None, for the Qt-default theme.
        """

        super().__init__()

        close_removed = (self.windowFlags().value -  # type: ignore
                         Qt.WindowType.WindowCloseButtonHint.value)
        self.setWindowFlags(Qt.WindowType(close_removed))  # type: ignore
        self.setWindowTitle(title)  # type: ignore
        if _ICON_FILE_PATH:
            self.setWindowIcon(QIcon(_ICON_FILE_PATH))  # type: ignore

        self._worker = worker
        self._widget_theme = widget_theme

        self._setup_ui()
        self._setup_connections()

        self._create_worker_thread()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._lblMain = QLabel(parent=None)
        self._pbMain = QProgressBar()
        self._pbMain.setFixedWidth(500)
        self._lblSub = QLabel(parent=None)
        self._pbSub = QProgressBar()
        self._pbSub.setFixedWidth(500)
        self._btnCancel = QPushButton('Cancel')

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._lblMain)
        self._vloMainLayout.addWidget(self._pbMain)
        self._vloMainLayout.addWidget(self._lblSub)
        self._vloMainLayout.addWidget(self._pbSub)
        self._vloMainLayout.addWidget(self._btnCancel)
        self.setLayout(self._vloMainLayout)  # type: ignore

        # Further initializations
        if not self._worker.nested:
            self._lblSub.hide()
            self._pbSub.hide()

        if _USE_THEME:
            set_widget_theme(self)  # type: ignore

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._worker.sig_new_process_unit, self._lblMain.setText)
        qt_connect(self._worker.sig_main_progress, self._pbMain.setValue)

        if self._worker.nested:  # The worker shouldn't have these if not nested
            qt_connect(self._worker.sig_new_subprocess_unit,
                       self._lblSub.setText)
            qt_connect(self._worker.sig_sub_progress, self._pbSub.setValue)

        qt_connect(self._worker.sig_finished, self._quit_thread)
        qt_connect(self._btnCancel.clicked, self._cancel_process)

    @property
    def theme(self) -> ThemeParameters:
        """ Returns the parameters of the theme set for this object. """

        return self._widget_theme

    @theme.setter
    def theme(self, new_theme: ThemeParameters) -> None:
        """ Sets a new set of parameters defining a theme to this object. """

        self._widget_theme = new_theme

    def _create_worker_thread(self) -> None:
        """ Creates a new thread and moves the worker there. """

        self._worker_thread = QThread()  # type: ignore
        self._worker_thread.start()
        self._worker.moveToThread(self._worker_thread)
        self._worker.sig_start.emit()

    def _quit_thread(self) -> None:
        """ Closes the thread after the worker has finished. """

        self._worker_thread.quit()
        self._worker_thread.wait()
        self.close()  # type: ignore

    def _cancel_process(self) -> None:
        """ Asks for confirmation to cancel the process. """

        reply = QMessageBox.question(self, 'Cancel Process',  # type: ignore
                                     "Are you sure you want to cancel "
                                     "the process?",
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._worker.sig_cancel.emit()


class ProgressDialog(_ProgressMixin, QDialog):
    """
    A dialog reporting on the progress of a process running on a separate
    thread.
    """

    def __init__(self, worker: QObject, title="Progress report",
                 widget_theme=None) -> None:
        """ Initializer for the class.

        :param worker: A worker subclassing QObject, handling a process.
        :param title: The title to set for the dialog. The default is
            "Progress report".
        :param widget_theme: A widget theme from the 'theme' module. The default
            is None, for the Qt-default theme.
        """

        super().__init__(worker, title, widget_theme)


class ProgressDW(_ProgressMixin, QDockWidget):
    """
    A dock widget reporting on the progress of a process running on a separate
    thread.
    """

    def __init__(self, worker: QObject, title="Progress report",
                 widget_theme=None) -> None:
        """ Initializer for the class.

        :param worker: A worker subclassing QObject, handling a process.
        :param title: The title to set for the dialog. The default is
            "Progress report".
        :param widget_theme: A widget theme from the 'theme' module. The default
            is None, for the Qt-default theme.
        """

        super().__init__(worker, title, widget_theme)

        self._wdgContent = QWidget()  # type: ignore
        self._wdgContent.setLayout(self._vloMainLayout)
        self.setWidget(self._wdgContent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFloating(True)


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
        self._btnToggleTheme = QPushButton("Toggle theme (enabled)")
        self._btnSimplePD = QPushButton("Open a simple progress dialog")
        self._btnSimplePD.setObjectName('simple_d')
        self._btnSimplePDW = QPushButton("Open a simple progress DW")
        self._btnSimplePDW.setObjectName('simple_dw')
        self._btnNestedPD = QPushButton("Open a nested process dialog")
        self._btnNestedPD.setObjectName('nested_d')
        self._btnNestedPDW = QPushButton("Open a nested process DW")
        self._btnNestedPDW.setObjectName('nested_dw')

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnToggleTheme)
        self._vloMainLayout.addWidget(self._btnSimplePD)
        self._vloMainLayout.addWidget(self._btnSimplePDW)
        self._vloMainLayout.addWidget(self._btnNestedPD)
        self._vloMainLayout.addWidget(self._btnNestedPDW)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        qt_connect(self._btnToggleTheme.clicked, self._slot_toggle_theme)
        qt_connect(self._btnSimplePD.clicked, self._slot_test)
        qt_connect(self._btnNestedPD.clicked, self._slot_test)
        qt_connect(self._btnSimplePDW.clicked, self._slot_test)
        qt_connect(self._btnNestedPDW.clicked, self._slot_test)

    def _slot_toggle_theme(self) -> None:
        """ Unlocks the theme module to test the theming of the PD. """

        global _USE_THEME
        _USE_THEME = not _USE_THEME
        self._btnToggleTheme.setText(f"Toggle theme ("
                                     f"{'enabled' if _USE_THEME
                                        else 'disabled'})")

    def _slot_test(self) -> None:
        """ Tests the progress dialogs/dock widgets. """

        def catch_signal() -> None:
            """
            Catches the finished signal of the worker object.
            Also emitted when the process is cancelled.
            """

            print("Worker object's process is finished!")

        wo = _Threaded('nested' in self.sender().objectName())
        wo.sig_finished.connect(catch_signal)
        theme = None if not _USE_THEME else WidgetTheme.yellow
        if 'dw' in self.sender().objectName():
            self._test = ProgressDW(wo, "Custom title", theme)
        else:
            self._test = ProgressDialog(wo, "Custom title", theme)

        starter = 'show' if 'dw' in self.sender().objectName() else 'exec'
        self._test.setWindowModality(Qt.WindowModality.ApplicationModal)
        getattr(self._test, starter)()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # type: ignore
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
