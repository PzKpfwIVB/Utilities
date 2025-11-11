""" Test cases for the colours module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.colours import *
from utils_qt_mk.creators import _CreatorCentre


@pytest.fixture
def widget__CreatorCentre(qtbot):
    cc = _CreatorCentre()
    qtbot.addWidget(cc)

    return cc


def test__CreatorCentre(qtbot, widget__CreatorCentre) -> None:

    # [TEST] Basic test for ColourScaleCreator; tested more in test_colours
    def handle_csc():
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_ColourScaleCreator = next(w for w in tops if
                                      getattr(w, 'windowTitle', lambda: '')()
                                      == "Colour scale creator")
        qtbot.addWidget(wdg_ColourScaleCreator)

        # [MOCK] Simulated selections
        colour = Colours.navyblue
        lwi = QListWidgetItem(colour.colour_box(), colour.name)
        wdg_ColourScaleCreator._lwColours.addItem(lwi)  # type: ignore
        wdg_ColourScaleCreator._slot_update_total_steps()
        assert (wdg_ColourScaleCreator.  # type: ignore
                _lwColours.item(0).text() == 'navyblue')

        wdg_ColourScaleCreator._btnCancel.click()

    QTimer.singleShot(0, handle_csc)  # type: ignore
    widget__CreatorCentre._btnColourScaleCreator.click()

    # [TEST] Basic test for _FileDialogDataEditor;
    # tested more in test_custom_file_dialog
    def handle_fdde():
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_FileDialogDataEditor = next(w for w in tops if
                                        getattr(w, 'windowTitle', lambda: '')()
                                        == "File dialog data editor")
        qtbot.addWidget(wdg_FileDialogDataEditor)

        # [TEST] Check default state
        assert (wdg_FileDialogDataEditor.
                _cmbPathCategory.currentText() == 'Source')
        assert (wdg_FileDialogDataEditor.
                _cmbDialogTypes.currentText() == "Open file name")

        # [TEST] Change the selected type
        wdg_FileDialogDataEditor._cmbTypeList.setCurrentIndex(0)
        assert (wdg_FileDialogDataEditor.
                _cmbPathCategory.currentText() == 'Destination')
        assert (wdg_FileDialogDataEditor.
                _cmbDialogTypes.currentText() == "Save file name")

        wdg_FileDialogDataEditor.close()

    QTimer.singleShot(0, handle_fdde)  # type: ignore
    widget__CreatorCentre._btnFileDialogCreator.click()

    # [TEST] Basic test for _MessageBoxTypeCreator; tested more in test_message
    def handle_mbtc():
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_MBTCreator = next(w for w in tops if
                              getattr(w, 'windowTitle', lambda: '')()
                              == "MBT Creator")
        qtbot.addWidget(wdg_MBTCreator)

        # [TEST] Check default state
        assert (wdg_MBTCreator.
                _cmbCategories.currentText() == 'critical')
        assert (wdg_MBTCreator.
                _oslButtons._lwSelection.item(0).text() == 'Ok')

        # [TEST] Change the selected type
        wdg_MBTCreator._cmbCategories.setCurrentIndex(2)
        assert (wdg_MBTCreator.
                _cmbCategories.currentText() == 'question')
        assert (wdg_MBTCreator.
                _oslButtons._lwSelection.item(0).text() == 'Yes')

        wdg_MBTCreator.close()

    QTimer.singleShot(0, handle_mbtc)  # type: ignore
    widget__CreatorCentre._btnMBTCreator.click()

    # [TEST] Basic test for ThemeCreator; tested more in test_theme_creator
    def handle_tc():
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_ThemeCreator = next(w for w in tops if
                                getattr(w, 'windowTitle', lambda: '')()
                                == "Theme creator")
        qtbot.addWidget(wdg_ThemeCreator)

        # [TEST] Check default state
        assert wdg_ThemeCreator._chkUseExistingTheme.isChecked() is True
        assert wdg_ThemeCreator._cslist[0]._chkSelector.isEnabled() is False

        # [TEST] Change the selected type
        wdg_ThemeCreator._chkUseExistingTheme.setChecked(False)
        assert wdg_ThemeCreator._chkUseExistingTheme.isChecked() is False
        assert wdg_ThemeCreator._cslist[0]._chkSelector.isEnabled() is True

        wdg_ThemeCreator.close()

    QTimer.singleShot(0, handle_tc)  # type: ignore
    widget__CreatorCentre._btnThemeCreator.click()
