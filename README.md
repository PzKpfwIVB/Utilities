# Utilities
## Overview

A package for collecting utilities I usually use in my Qt-projects in Python.
Some modules depend on others but some can be used on their own. Some modules
might have stub files to assist development, but they always contain an
initializer function to create the necessary stub files if they are missing
when the module is first imported. The functionality of subclasses of `QDialog`
are also available as subclasses of `QDockWidget` (floating, same-window
dialogs). There are no set goals for this project other than having these things
in one place, in a structured manner.

The package can be installed via pip:
```
pip install utils-qt-mk
```

Then it can be used as `utils_qt_mk`, for example
```python
from utils_qt_mk.colours import ColourSelector
```

## Contents
### general

General functions, classes etc. mostly for internal use in other parts of the
package. Modules usually depend on it.

### config

A module for setting up constants for the package. Provides getter/setter
functions.

### colours

Adds the [standard R colour palette](https://r-charts.com/colors/) to Qt applications. It provides a
singleton object named `Colours`, with attribute access to all the colours of
R's `colors()` function. These can be conveniently selected from a colour
selector dialog, either from a drop-down list (by name) or from a grid (by
visual selection). Based on this selector there is a colour scale creator
dialog, where from a number of selected colours and set number of steps a colour
scale can be defined for further use e.g. for plotting. It optionally uses
**theme**: if the module can be imported, the dialogs can have a theme.

To get a list of `QColor` objects from an existing scale, use the
`scale_json_to_list()` function.

### creators

Provides a simple way to use creators of other modules. Importing and running
the `creator_centre()` function opens the Creator Centre, a simple app where all
these creators are available. If new file dialogs or message boxes are defined,
the stub file must be deleted so the new types could be included (might become
automatic in the future).

### custom_file_dialog

Provides predefined file dialogs (`CFDType` singleton) customized by a JSON
file and a creator dialog. In the latter, a custom dialog could be defined,
setting its type (source/destination), window title, dialog type (to open/save a
file or open an existing directory), extension filter and associated path.
Another function of these dialogs is to provide navigation history: if a path is
successfully selected, the JSON file gets updated with it.

To get a list of available path types, use the `get_cfd_types()` function.

### message

Provides predefined message boxes (`MessageBoxType` singleton) that can have a
theme assigned (so it depends on **theme**) and a creator dialog. In the latter,
a custom message box can be defined, setting its category (e.g. warning),
window title and message (text content of the message box). A 'custom' category
message box can also have its icon, buttons and flags set.

To get a list of available messagebox types, use the `get_messagebox_types()`
function.

### progress_dialog

Provides a cancellable, optionally nested progress dialog, reporting on a
compatible process ran by a `QObject`-subclass on a separate thread. It also has
a (package private) example of a compatible worker object. It optionally uses
**theme**: if the module can be imported, it can use the preset themes.

### theme

Provides a simple way to apply a predefined theme to Qt-widgets. It also adds a
singleton object named `WidgetTheme` that has attribute access to all the
defined themes. The `set_widget_theme()` function uses this singleton to select
a theme.

To get a list of available themes, use the `get_theme_types()` function.

### theme_creator

Depends on **theme** and **colours** to provide a theme creator dialog. It
provides a simple interface to edit and preview existing themes or to create new
ones.


### widget_mix

A module for a mix of custom widgets.

## Wiki

For a more detailed API reference, see the project wiki.
