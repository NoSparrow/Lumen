Lumen – Monitor Brightness Adjustment Application

Description:
Lumen is a graphical application written in Python (PySide6) that allows you to discover and manage monitors connected to your system.
It allows you to adjust the brightness:
- hardware (DDC/CI)
- software (xrandr)
It supports multiple monitors and remembers user settings.

Installation:

After installing the .deb package, the application is available in the menu under the name "Lumen"

Running:
- Click the icon in the menu to launch the GUI.
- Can be run in a terminal: `lumen --terminal`

Requirements:
- Python 3.12 or newer
- Internet connection during installation (for automatic setup of PySide6)
- Virtual environment will be created automatically in /usr/share/lumen/venv
- ddcutil
- x11-xserver-utils

Repository:

https://github.com/NoSparrow/Lumen
