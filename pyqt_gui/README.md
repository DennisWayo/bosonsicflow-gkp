# bosonicflow-gkp desktop app (PySide6)

This folder contains a cross-platform desktop playground for the BosonicFlow-GKP series.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the app with `python main.py`.

## Build a ZIP per OS

These builds must be created on the target OS.

1. Install PyInstaller with `pip install pyinstaller`.
2. Run the PyInstaller command.
Mac or Linux: `pyinstaller --noconfirm --clean --windowed --name bosonicflow-gkp --icon assets/icon.svg --add-data "assets/icon.svg:assets" main.py`.
Windows (PowerShell): `pyinstaller --noconfirm --clean --windowed --name bosonicflow-gkp --icon assets/icon.svg --add-data "assets/icon.svg;assets" main.py`.
3. Zip the output folder in `dist/bosonicflow-gkp/`.

Notes:
- The app embeds its own Python and dependencies when built with PyInstaller.

## macOS quick build

From this folder, run `./build_macos.sh`. If you want a specific interpreter, set `PYTHON_BIN` first.

## Linux quick build

From this folder, run `./build_linux.sh`. If you want a specific interpreter, set `PYTHON_BIN` first.

## Windows quick build

From PowerShell, run `.\build_windows.ps1`. If you want a specific interpreter, set `$env:PYTHON_BIN` first.
