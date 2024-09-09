""" A cancellable, optionally nested progress dialog, reporting on a compatible
process ran by a QObject-subclass on a separate thread. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
import sys

# Qt6 modules
from PySide6.QtCore import *
from PySide6.QtWidgets import *

# Custom modules
try:
    from utils.theme import set_widget_theme, ThemeParameters, WidgetTheme
    _USE_THEME = True
except ImportError:
    _USE_THEME = False


class _Threaded(QObject):
    """ An example, progress dialog compatible class.
    Worker objects of simple (not nested) PDs do not need sub-signals. """

    sig_new_process_unit = Signal(str)
    sig_new_subprocess_unit = Signal(str)
    sig_main_progress = Signal(int)
    sig_sub_progress = Signal(int)
    sig_finished = Signal()  # This should carry the returned value of the proc.
    sig_start = Signal()
    sig_cancel = Signal()

    def __init__(self, nested=False):
        """ Initializer for the class.

        Parameters
        ----------
        nested: bool
            A flag marking whether the progress dialog should be nested.
            The default is False.
        """

        super().__init__()

        self._nested = nested
        self._canceled = False

        self.sig_start.connect(self._process)
        self.sig_cancel.connect(self._cancel_process)

    @property
    def nested(self) -> bool:
        return self._nested

    @Slot()
    def _process(self) -> None:
        """ The slot connected to the start signal.
        Emits 'sig_finished' when the process finishes."""

        if self._nested:
            for i in range(4):
                self.sig_new_process_unit.emit(f'Outer Iteration {i+1}')
                for j in range(6):
                    self.sig_new_subprocess_unit.emit(f'Inner Iteration {j+1}')
                    self.sig_main_progress.emit((i + 1) * 25)
                    self.sig_sub_progress.emit((j + 1) * 100/6)
                    QThread.msleep(1000)
                    QCoreApplication.processEvents()  # To catch cancellation
                    if self._canceled:
                        break
                if self._canceled:
                    break
        else:
            for i in range(4):
                self.sig_new_process_unit.emit(f'Iteration {i+1}')
                self.sig_main_progress.emit((i + 1) * 25)
                QThread.msleep(1000)
                QCoreApplication.processEvents()  # To catch cancellation
                if self._canceled:
                    break
        self.sig_finished.emit()

    @Slot()
    def _cancel_process(self) -> None:
        """ The slot connected to the cancel signal.
        Needs the button press event to be processed beforehand. """

        self._canceled = True


class ProgressDialog(QDialog):
    """ A dialog reporting on the progress of a process running
    on a separate thread. """

    def __init__(self, worker, title="Progress report", widget_theme=None):
        """ Initializer for the class.

        worker : QObject
            A worker subclassing QObject, handling a process.

        title : str, optional
            The title to set for the dialog. The default is "Progress report".

        widget_theme : WidgetTheme, optional
            A widget theme from the 'theme' module. To use, 'unlock_theme()'
            on the module. The default is None, for the locked module.
        """

        super().__init__()

        close_removed = (self.windowFlags().value -
                         Qt.WindowType.WindowCloseButtonHint.value)
        self.setWindowFlags(Qt.WindowType(close_removed))
        self.setWindowTitle(title)

        self._worker = worker
        self._widget_theme = widget_theme

        self._setup_ui()
        self._setup_connections()

        self._create_worker_thread()

    def _setup_ui(self) -> None:
        """ Sets up the user interface: GUI objects and layouts. """

        # GUI objects
        self._lblMain = QLabel()
        self._pbMain = QProgressBar()
        self._pbMain.setFixedWidth(500)
        self._lblSub = QLabel()
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
        self.setLayout(self._vloMainLayout)

        # Further initializations
        if not self._worker.nested:
            self._lblSub.hide()
            self._pbSub.hide()

        if _USE_THEME:
            set_widget_theme(self)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._worker.sig_new_process_unit.connect(self._lblMain.setText)
        self._worker.sig_main_progress.connect(self._pbMain.setValue)

        if self._worker.nested:  # The worker shouldn't have these if not nested
            self._worker.sig_new_subprocess_unit.connect(self._lblSub.setText)
            self._worker.sig_sub_progress.connect(self._pbSub.setValue)

        self._worker.sig_finished.connect(self._quit_thread)
        self._btnCancel.clicked.connect(self._cancel_process)

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

        self._worker_thread = QThread()
        self._worker_thread.start()
        self._worker.moveToThread(self._worker_thread)
        self._worker.sig_start.emit()

    def _quit_thread(self) -> None:
        """ Closes the thread after the worker has finished. """

        self._worker_thread.quit()
        self._worker_thread.wait()
        self.close()

    def _cancel_process(self) -> None:
        """ Asks for confirmation to cancel the process. """

        reply = QMessageBox.question(self, 'Cancel Process',
                                     "Are you sure you want to cancel "
                                     "the process?",
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._worker.sig_cancel.emit()


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
        self._btnToggleTheme = QPushButton("Toggle theme")
        self._btnSimplePD = QPushButton("Open a simple progress dialog")
        self._btnSimplePD.setObjectName('simple')
        self._btnNestedPD = QPushButton("Open a nested process dialog")
        self._btnNestedPD.setObjectName('nested')

        # Layouts
        self._vloMainLayout = QVBoxLayout()
        self._vloMainLayout.addWidget(self._btnToggleTheme)
        self._vloMainLayout.addWidget(self._btnSimplePD)
        self._vloMainLayout.addWidget(self._btnNestedPD)

        self._wdgCentralWidget = QWidget()
        self._wdgCentralWidget.setLayout(self._vloMainLayout)
        self.setCentralWidget(self._wdgCentralWidget)

    def _setup_connections(self) -> None:
        """ Sets up the connections of the GUI objects. """

        self._btnToggleTheme.clicked.connect(self._slot_toggle_theme)
        self._btnSimplePD.clicked.connect(self._slot_pd_test)
        self._btnNestedPD.clicked.connect(self._slot_pd_test)

    @staticmethod
    def _slot_toggle_theme() -> None:
        """ Unlocks the theme module to test the theming of the PD. """

        global _USE_THEME
        _USE_THEME = not _USE_THEME

    def _slot_pd_test(self) -> None:
        """ Tests the progress dialogs. """

        def catch_signal() -> None:
            """ Catches the finished signal of the worker object.
            Also emitted when the process is cancelled.
            """

            print("Worker object's process is finished!")

        wo = _Threaded(self.sender().objectName() == 'nested')
        wo.sig_finished.connect(catch_signal)
        theme = None if not _USE_THEME else WidgetTheme.yellow
        dialog = ProgressDialog(wo, "Custom title", theme)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = _TestApplication()
    mainWindow.show()
    app.exec()
