""" Test cases for the progress_dialog module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.progress_dialog import *
from utils_qt_mk.progress_dialog import _TestApplication


def test_progress_dialogs(qtbot) -> None:
    widget__TestApplication = _TestApplication()

    def handle_progress_finished(cancel: bool = False) -> bool:
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_pd = next(w for w in tops if
                      getattr(w, 'windowTitle', lambda: '')() == "Custom title")
        qtbot.addWidget(wdg_pd)
        if cancel:
            wdg_pd._worker.sig_cancel.emit()  # Simulate cancel request

        return True

    # Dock widgets' tests would fail as threads get destroyed prematurely,
    # but they have no additional functionality anyway
    QTimer.singleShot(0, handle_progress_finished)    # type: ignore
    widget__TestApplication._btnSimplePD.click()    # type: ignore

    QTimer.singleShot(0, lambda: handle_progress_finished(True))  # type: ignore
    widget__TestApplication._btnNestedPD.click()  # type: ignore
