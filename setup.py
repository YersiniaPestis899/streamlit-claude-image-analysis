from setuptools import setup

APP = ['claude_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PySide6'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui'],
    'excludes': ['PyInstaller'],  # PyInstallerを除外
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
