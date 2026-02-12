import os
import sys
import winreg


class StartupManager:
    APP_NAME = "TimeReporter"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def set_startup(enabled: bool):
        """Enable or disable startup with Windows."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                StartupManager.REG_PATH,
                0,
                winreg.KEY_SET_VALUE,
            )

            if enabled:
                # Use the current executable path
                # If running as script, sys.executable is python.exe, we need the script path too
                # If running as EXE (PyInstaller), sys.executable is the EXE path
                if getattr(sys, "frozen", False):
                    path = sys.executable
                else:
                    path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

                winreg.SetValueEx(key, StartupManager.APP_NAME, 0, winreg.REG_SZ, path)
            else:
                try:
                    winreg.DeleteValue(key, StartupManager.APP_NAME)
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    @staticmethod
    def is_startup_enabled():
        """Check if startup is currently enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, StartupManager.REG_PATH, 0, winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, StartupManager.APP_NAME)
                enabled = True
            except FileNotFoundError:
                enabled = False
            winreg.CloseKey(key)
            return enabled
        except Exception:
            return False
