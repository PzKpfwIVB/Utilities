# Utilities #
## Overview ##

A package for collecting utilities I usually use in my Qt-projects in Python. Some modules depend on others but some can be used on their own. Some modules might have stub files to assist development, but they always contain an initializer function to create the necassary stub files if they are missing when the module is first imported. The functionality of subclasses of QDialog are also available as subclasses of QDockWidget (floating, same-window dialogs). There are no set goals for this project other than having these things in one place, in a structured manner.

## Contents ##
### _general ###

General functions, classes etc. for internal use in other parts of the package. Modules usually depend on it.

### colours ###

Adds the [standard R colour palette](https://r-charts.com/colors/) to Qt applications. It provides a singleton object named Colours, with attribute access to all the colours of R's *colors()* function. These can be conveniently selected from a colour selector dialog, either from a drop-down list (by name) or from a grid (by visual selection). Based on this selector there is a colour scale creator dialog, where from a number of selected colours and set number of steps a colour scale can be defined for further use e.g. for plotting. It optionally uses **theme**: if the module can be imported, the dialogs can have a theme.

### custom_file_dialog ###

Provides predefined file dialogs (PythTypes singleton) customized by a JSON file and a creator dialog. In the latter, a custom dialog could be defined, setting its type (source/destination), window title, dialog type (to open/save a file or open an existing directory), extension filter and associated path. Another function of these dialogs is to provide navigation history: if a path is successfully selected, the JSON file gets updated with it.

### message ###

Provides predefined message boxes (MessageBoxType singleton) that can have a theme assigned (so it depends on **theme**) and a creator dialog. In the latter, a custom message box can be defined, setting it category (e.g. warning), window title and message (text content if the message box). A 'custom' category message box can also have its icon, buttons and flags set.

### progress_dialog ###

Provides a cancellable, optionally nested progress dialog, reporting on a compatible process ran by a QObject-subclass on a separate thread. It also has a (package private) example of a compatible worker object. It optionally uses **theme**: if the module can be imported, it can use the preset themes.

### theme ###

Provides a simple way to apply a predefined theme to Qt-widgets. It also adds a singleton object named WidgetTheme that has attribute access to all the defined themes. The *set_widget_theme()* function uses this singleton to select a theme.

### theme_creator ###

Depends on **theme** and **colours** to provide a theme creator dialog. It provides a simple interface to edit and preview existing themes or to create new ones.