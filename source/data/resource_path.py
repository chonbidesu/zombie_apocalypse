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