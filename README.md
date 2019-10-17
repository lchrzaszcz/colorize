========
Colorize
========

Colorize - terminator plugin for coloring title bar and background of each terminal separately

Screenshot
==========

![Alt text](/terminator-colorize.png?raw=true "Colorize screenshot")

Installation
============

1. Copy colorize.py to plugin directory in terminator installation (for example: `/usr/share/terminator/terminatorlib/plugins` or ` ~/.config/terminator/plugins/`)
2. Enable plugin in plugin preferences (Right click on terminator > Preferences > Plugins > click colorize)

How to use
==========

1. Launch terminator (obvious :P)
2. Right-click on terminal and
   - choose "Choose color" to set custom color or
   - choose some preset color from "Pick color" submenu or
   - choose "Colorize background" to set background of the terminal according to the title bar color
   - choose "Restore background" to reset the background to its default value

Bugs
====

Shortcuts for "Pick color" don't work yet

ToDo
====

1. Make shortcuts for "Pick color" work :P
2. Some kind of GUI
3. Instruction for configuration of plugin in text-mode
4. Inherit colors after splitting