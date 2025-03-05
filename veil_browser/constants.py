import os
import json

def load_icon_paths():
    """Load icon paths from JSON file"""
    try:
        with open(os.path.join('data', 'icons.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading icons.json: {e}")
        return {
            "back": "icons/back.png",
            "forward": "icons/forward.png",
            "refresh": "icons/refresh.png",
            "windowMinimize": "icons/window-minimize.png",
            "windowMaximize": "icons/window-maximize.png",
            "windowClose": "icons/window-close.png"
        }

ICON_PATHS = load_icon_paths()
HISTORY_FILE = os.path.join('data', 'history.json')