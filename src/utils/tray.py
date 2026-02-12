import sys
from PIL import Image
import os
from src.utils.resources import get_resource_path


class TrayIcon:
    def __init__(self, on_show, on_exit, on_toggle_break=None):
        self.on_show = on_show
        self.on_exit = on_exit
        self.on_toggle_break = on_toggle_break
        self.icon = None
        self.is_on_break = False
        self._setup_tray()

    def _get_icon_image(self):
        icon_path = get_resource_path("Time Reporter.png")
        if os.path.exists(icon_path):
            return Image.open(icon_path)

        # Fallback to generated image
        width = 64
        height = 64
        color1 = "#24a0ed"  # Blue
        color2 = "#1f538d"  # Darker Blue
        image = Image.new("RGB", (width, height), color2)
        from PIL import ImageDraw

        dc = ImageDraw.Draw(image)
        dc.rectangle(
            [width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=color1
        )
        return image

    def _toggle_break_internal(self, icon, item):
        if self.on_toggle_break:
            self.is_on_break = self.on_toggle_break()
            if self.is_on_break:
                self.notify("Time Reporter", "Mola Başladı - Mola süresi kaydediliyor.")
            else:
                self.notify("Time Reporter", "Çalışma Başladı - Takip sistemi aktif.")
            # The menu items update dynamically when the menu is shown again
            # as long as we use a function for the title or recreate the menu.

    def _setup_tray(self):
        import pystray

        def get_break_label(item):
            return "Molayı Durdur" if self.is_on_break else "Mola Ver"

        menu = pystray.Menu(
            pystray.MenuItem("Show Dashboard", self.on_show),
            pystray.MenuItem(get_break_label, self._toggle_break_internal),
            pystray.MenuItem("Exit", self.on_exit),
        )
        self.icon = pystray.Icon(
            "TimeReporter", self._get_icon_image(), "Time Reporter", menu
        )

    def run(self):
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def notify(self, title, message):
        if self.icon:
            self.icon.notify(message, title)
