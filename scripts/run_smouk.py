"""
SMOUK by Shadow Coders — development launcher.

Runs openshot-qt using the locally-built libopenshot bindings and the MSYS2
MinGW64 Python + PyQt5 toolchain.

Usage:
    C:\msys64\mingw64\bin\python.exe scripts\run_smouk.py
    (or double-click scripts\run_smouk.bat)
"""

import os
import sys

# Workspace root (parent of the scripts/ directory)
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MSYS2_BIN = r"C:\msys64\mingw64\bin"

# DLL directories required by the built libopenshot bindings.
# On Python 3.8+, extension-module DLLs are resolved via add_dll_directory(),
# not via PATH.
_DLL_DIRS = [
    MSYS2_BIN,
    os.path.join(WORKSPACE, "libopenshot", "build", "src"),
    os.path.join(WORKSPACE, "libopenshot-audio", "build"),
]
for _d in _DLL_DIRS:
    if os.path.isdir(_d):
        os.add_dll_directory(_d)

# libopenshot Python bindings + openshot-qt source
sys.path.insert(0, os.path.join(WORKSPACE, "libopenshot", "build", "bindings", "python"))
sys.path.insert(0, os.path.join(WORKSPACE, "openshot-qt", "src"))

# Force PyQt5 (matches the Qt5 build of libopenshot)
os.environ.setdefault("OPENSHOT_QT_API", "pyqt5")

import launch

launch.main()
