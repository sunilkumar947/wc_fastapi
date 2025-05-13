from PyQt6.QtCore import QObject, pyqtSignal
from pystray import Icon, Menu, MenuItem
from PIL import Image

class TrayHandler(QObject):
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()
    exit_signal = pyqtSignal()

    def __init__(self, icon_path):
        super().__init__()
        self.icon_path = icon_path

    def setup_tray(self):
        """Set up the system tray using pystray."""
        image = Image.open(self.icon_path)
        self.icon = Icon(
            "Work Tracker",
            image,
            menu=Menu(
                MenuItem("Show", self.on_show),
                MenuItem("Hide", self.on_hide),
                MenuItem("Exit", self.on_exit),
            ),
        )
        self.icon.run()

    def on_show(self):
        self.show_signal.emit()

    def on_hide(self):
        self.hide_signal.emit()

    def on_exit(self):
        self.exit_signal.emit()
        self.icon.stop()
