import sys
import os
from PySide6.QtWidgets import QApplication
from gui import LumenWindow
import subprocess
from monitors import get_monitors

monitors = get_monitors()

app = QApplication(sys.argv)

if monitors:
    window = LumenWindow(monitors)
    window.show()
    sys.exit(app.exec())
else:
    print("No monitors to display or other error")










 










