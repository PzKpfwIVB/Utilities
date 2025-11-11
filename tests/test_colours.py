""" Test cases for the colours module. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
import os

# Other 3rd-party modules
import pytest

# Custom modules/classes
from utils_qt_mk.colours import *


def test_scale_json_to_list() -> None:
    rgb_list = [(182, 1, 0), (185, 7, 0), (188, 13, 0),
                (191, 19, 0), (194, 25, 0), (197, 31, 0),
                (200, 37, 0), (204, 43, 0), (207, 49, 0),
                (210, 55, 0), (213, 62, 0), (216, 68, 0),
                (219, 74, 0), (222, 80, 0), (226, 86, 0),
                (229, 92, 0), (232, 98, 0), (235, 104, 0),
                (238, 110, 0), (241, 116, 0), (245, 123, 0),
                (244, 128, 0), (244, 134, 0), (243, 140, 0),
                (243, 146, 0), (242, 152, 0), (242, 158, 0),
                (241, 163, 0), (241, 169, 0), (240, 175, 0),
                (240, 181, 0), (240, 187, 0), (239, 193, 0),
                (239, 199, 0), (238, 204, 0), (238, 210, 0),
                (237, 216, 0), (237, 222, 0), (236, 228, 0),
                (236, 234, 0), (236, 240, 0), (231, 237, 0),
                (226, 235, 0), (222, 233, 0), (217, 231, 0),
                (213, 229, 0), (208, 227, 0), (204, 225, 0),
                (199, 223, 0), (195, 221, 0), (190, 219, 0),
                (185, 217, 0), (181, 215, 0), (176, 213, 0),
                (172, 211, 0), (167, 209, 0), (163, 207, 0),
                (158, 205, 0), (154, 203, 0), (149, 201, 0),
                (145, 199, 0), (141, 195, 0), (137, 191, 0),
                (133, 187, 0), (129, 184, 0), (125, 180, 0),
                (121, 176, 0), (117, 172, 0), (113, 169, 0),
                (109, 165, 0), (105, 161, 0), (101, 157, 0),
                (97, 154, 0), (93, 150, 0), (89, 146, 0),
                (85, 142, 0), (81, 139, 0), (77, 135, 0),
                (73, 131, 0), (69, 127, 0), (65, 124, 0)]
    expected = [QColor(*rgb) for rgb in rgb_list]  # type: ignore

    assert scale_json_to_list(os.path.join(os.path.split(__file__)[0],
                                           '1_to_5.json')) == expected


@pytest.mark.parametrize('colour, expected', [
    (Colour(), {'name': 'white',
                'as_tuple': (255, 255, 255),
                'as_hex': '#FFFFFF',
                'as_qt': QColor(255, 255, 255),  # type: ignore
                'as_qt_neg': QColor(0, 0, 0),  # type: ignore
                'text_col': Qt.GlobalColor.black}),
    (Colour('dark_blue', 40, 50, 100),
     {'name': 'dark_blue',
      'as_tuple': (40, 50, 100),
      'as_hex': '#283264',
      'as_qt': QColor(40, 50, 100),   # type: ignore
      'as_qt_neg': QColor(215, 205, 155),  # type: ignore
      'text_col': Qt.GlobalColor.white})])
def test_Colour(colour: Colour, expected: dict) -> None:
    assert colour.name == expected['name']
    assert tuple(colour) == expected['as_tuple']  # type: ignore
    assert colour.as_hex == expected['as_hex']
    assert colour.as_qt() == expected['as_qt']
    assert colour.as_qt(negative=True) == expected['as_qt_neg']
    assert colour.text_colour() == expected['text_col']


@pytest.mark.parametrize('name, expected', [
    ('cornsilk4', 65),
    ('darkseagreen', 99),
    ('grey59', 207)
])
def test__Colours_index(name: str, expected: int) -> None:
    assert Colours.index(name) == expected

@pytest.mark.parametrize('idx, expected', [
    (65, Colour('cornsilk4', 120, 118, 99)),
    (99, Colour('darkseagreen', 131, 176, 119)),
    (207, Colour('grey59', 132, 132, 132))
])
def test__Colours_colour_at(idx: int, expected: Colour) -> None:
    assert Colours.colour_at(idx) == expected


@pytest.mark.parametrize('qcolor, expected', [
    (QColor(40, 50, 100),   # type: ignore
     Colour('unnamed', 40, 50, 100)),
    (QColor(113, 77, 202),    # type: ignore
     Colour('mediumpurple3', 113, 77, 202))
])
def test__Colours_from_qt(qcolor: QColor, expected: Colour) -> None:
    assert Colours.from_qt(qcolor) == expected


@pytest.fixture
def widget_ColourSelector(qtbot):
    w = ColourSelector()
    qtbot.addWidget(w)

    return w


def test_ColourSelector(qtbot, widget_ColourSelector) -> None:
    # [TEST] Default state (simple)
    assert widget_ColourSelector._ledFilter.text() == ''  # type: ignore
    assert (widget_ColourSelector.  # type: ignore
            _cmbColourList.currentText() == 'white')

    # [TEST] Enter 'gre' and click the filter button
    widget_ColourSelector._ledFilter.setText('gre')  # type: ignore
    widget_ColourSelector._btnFilter.click()  # type: ignore
    assert (widget_ColourSelector.  # type: ignore
            _cmbColourList.currentText() == 'darkgreen')

    # [TEST] Enter 'pink' and hit return
    widget_ColourSelector._ledFilter.setText('pink')  # type: ignore
    qtbot.keyPress(widget_ColourSelector._ledFilter,  # type: ignore
                   Qt.Key.Key_Return)
    assert (widget_ColourSelector.  # type: ignore
            _cmbColourList.currentText() == 'deeppink')

    # [TEST] Switch to the extended tab and check selection
    widget_ColourSelector._slot_tab_changed(1)
    qtbot.mousePress(widget_ColourSelector._colourBoxDrawer,  # type: ignore
                     Qt.MouseButton.LeftButton,
                     pos=QPoint(410, 270))  # type: ignore
    assert (widget_ColourSelector.  # type: ignore
            _lblCurrentColour.text() == "Selection: magenta4")

    # [TEST] Click apply which emits the selection
    def dummy_slot_apply(button_id: int, colour: Colour) -> bool:
        return button_id == 0 and colour == Colour('magenta4', 112, 0, 126)

    with qtbot.wait_signal(widget_ColourSelector.colourChanged,
                           check_params_cb=dummy_slot_apply):
        widget_ColourSelector._btnApply.click()  # type: ignore


@pytest.fixture
def widget_ColourScaleCreator(qtbot):
    w = ColourScaleCreator()
    qtbot.addWidget(w)

    return w


def test_ColourScaleCreator(qtbot, widget_ColourScaleCreator) -> None:
    # [TEST] Open the colour selector and select a colour (navy blue)
    def handle_modal_dialog():
        tops = QApplication.instance().topLevelWidgets()
        # Find child dialog by windowTitle
        wdg_ColourSelector = next(w for w in tops if
                                  getattr(w, 'windowTitle',
                                          lambda: '')() == "Colour selector")
        qtbot.addWidget(wdg_ColourSelector)
        wdg_ColourSelector._ledFilter.setText('navyblue')  # type: ignore
        wdg_ColourSelector._btnFilter.click()
        wdg_ColourSelector._btnApply.click()  # type: ignore

    QTimer.singleShot(0, handle_modal_dialog)    # type: ignore
    widget_ColourScaleCreator._btnAddColour.click()    # type: ignore
    assert (widget_ColourScaleCreator.    # type: ignore
            _lwColours.item(0).text() == 'navyblue')

    # [MOCK] Simulated selection
    colour = Colours.firebrick3
    lwi = QListWidgetItem(colour.colour_box(), colour.name)
    widget_ColourScaleCreator._lwColours.addItem(lwi)  # type: ignore
    widget_ColourScaleCreator._slot_update_total_steps()
    assert (widget_ColourScaleCreator.  # type: ignore
            _lwColours.item(1).text() == 'firebrick3')

    widget_ColourScaleCreator._spbSteps.setValue(4)  # type: ignore
    widget_ColourScaleCreator._btnUpdate.click()  # type: ignore
    # `paintEvent()` must be called manually because the window is hidden and
    # thus the scale would not be updated otherwise
    (widget_ColourScaleCreator.  # type: ignore
     _v_scale.paintEvent(QPaintEvent(QRect())))
    assert (widget_ColourScaleCreator.  # type: ignore
            _v_scale.scale_colours == [QColor(0, 1, 115),  # type: ignore
                                       QColor(36, 5, 97),  # type: ignore
                                       QColor(73, 10, 79),  # type: ignore
                                       QColor(109, 14, 61),  # type: ignore
                                       QColor(146, 19, 43),  # type: ignore
                                       QColor(183, 24, 26)  # type: ignore
                                       ])
