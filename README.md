# Utilities #
## Overview ##

A package for collecting utilities I usually use in my Qt-projects in Python. Some modules depend on others but some can be used on their own. There are no set goals for this project other than having these things in one place, in a structured manner.

## Contents ##
### _general ###

General functions, classes etc. for internal use in other parts of the package. Modules usually depend on it.

### colours ###

Adds the [standard R colour palette](https://r-charts.com/colors/) to Qt applications. It provides a singleton object named Colours, with attribute access to all the colours of R's *colors()* function. These can be conveniently selected from a colour selector dialog, either from a drop-down list (by name) or from a grid (by visual selection). Based on this selector there is a colour scale creator dialog, where from a number of selected colours and set numer of steps a colour scale can be defined for further use e.g. for plotting.

### theme ###

Provides a simple way to apply a predefined theme to Qt-widgets. It also adds a singleton object named WidgetTheme that has attribute access to all the defined themes. The *set_widget_theme()* function uses this singleton to select a theme.

### theme_creator ###

Depends on **theme** and **colours** to provide a theme creator dialog. It provides a simple interface to edit and preview existing themes or to create new ones.