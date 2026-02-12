import threading
import pystray
from PIL import Image, ImageDraw
import os


class TrayIcon:
    def __init__(self, on_show, on_exit):
        self.on_show = on_show
        self.on_exit = on_exit
        self.icon = None
        self._setup_tray()

    def _create_image(self):
        # Create a simple blue square icon
        width = 64
        height = 64
        color1 = "#24a0ed"  # Blue
        color2 = "#1f538d"  # Darker Blue

        image = Image.new("RGB", (width, height), color2)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            [width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=color1
        )
        return image

    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show Dashboard", self.on_show),
            pystray.MenuItem("Exit", self.on_exit),
        )
        self.icon = pystray.Icon(
            "TimeReporter", self._create_image(), "Time Reporter", menu
        )

    def run(self):
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def notify(self, title, message):
        if self.icon:
            self.icon.notify(message, title)
