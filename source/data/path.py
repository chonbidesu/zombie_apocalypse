# resource_path.py

import os
import sys

class ResourcePath:
    """Get the absolute path to a resource, working for both dev & PyInstaller."""
    def __init__(self, relative_path):
        self.path = self._get_path(relative_path)

    def _get_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):  # PyInstaller extracts files here in --onefile mode
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    

class SaveLoadPath:
    """Handles paths for saving/loading game states to a writable location."""
    def __init__(self, filename):
        # Use the user's AppData (Windows) or local share directory (Linux/Mac)
        if sys.platform == "win32":
            base_path = os.path.join(os.environ["APPDATA"], "ZombieApocalypse", "saves")
        else:
            base_path = os.path.join(os.path.expanduser("~"), ".local", "share", "ZombieApocalypse", "saves")

        # Ensure the save directory exists
        os.makedirs(base_path, exist_ok=True)

        self.path = os.path.join(base_path, filename)    