import sys, os

def get_file_path (relative_path):
    "Returns the appropriate file path, depending on whether the game is being ran in PyCharm or PyInstaller."

    try:
        # Happens when running in Pyinstaller
        base_path = sys._MEIPASS
    except Exception:
        # Happens when running in PyCharm
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)