# Mouser

## Description

**Mouser** is an open-source desktop application for collecting and analyzing data from animal experiments with minimal user interaction. It helps researchers record precise measurements in controlled lab environments where direct device handling is limited.

By integrating with lab equipment such as balances, calipers, and RFID chip readers, Mouser enables fast, touch-free data collection while providing immediate on-screen and sound-based confirmations — allowing scientists to focus entirely on their experiments.


## Key Features

- Connects with RFID readers, balances, and calipers for hands-free data collection  
- Supports creation and management of experiments in a unified desktop interface  
- Automatically identifies animals via RFID biochips  
- Provides sound and visual feedback for seamless lab workflows  
- Stores and manages experimental data using SQLite databases  

## Developer Setup

#### Machine Requirements

- **Python:** Version 3.9 or newer  
- **Operating Systems:** Best supported on Windows; compatible with macOS and Linux (minor UI differences)

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/oss-slu/Mouser.git

# 2. Navigate to project directory
cd Mouser

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Upgrade packaging tools (recommended)
python -m pip install --upgrade pip setuptools wheel

# 5. Install dependencies
python -m pip install -r requirements.txt

# 6. Run the application
python main.py
```

#### Windows note (Use Python 3.11 in `.venv`)

If your Windows machine has multiple Python versions (for example system `3.14`), create the project venv with `3.11` explicitly:

```powershell
cd Mouser
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -V
```

Expected output from the last command: `Python 3.11.x`

This only affects the project virtual environment, not your system Python.

When you are done working:

```bash
deactivate
```

#### macOS note (PyAudio)

If dependency installation fails on `pyaudio` with `portaudio.h file not found`, install PortAudio first:

```bash
brew install portaudio
python -m pip install pyaudio
```

#### macOS note (Tkinter startup/import errors)

If running `python main.py` fails with either of these:
- `ModuleNotFoundError: No module named '_tkinter'`
- `macOS 26 (2603) or later required, have instead 16 (1603) !`

your Python interpreter does not have a working Tk runtime for this app.

Use a Python build with Tk support (Python.org installer or Homebrew `python@3.11` + `python-tk@3.11`), then recreate the virtual environment:

```bash
cd Mouser
rm -rf .venv

# Option A: Python.org interpreter (example path)
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -m venv .venv

# Option B: Homebrew interpreter (if installed)
# /opt/homebrew/bin/python3.11 -m venv .venv

source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -c "import tkinter as tk; r=tk.Tk(); r.destroy(); print('tk ok')"
python main.py
```

If Homebrew `python3.11` is not installed yet:

```bash
brew install python@3.11 python-tk@3.11
```

#### macOS/Linux note (Virtual serial simulation)

The RFID simulator can use virtual serial port pairs:

- **Windows:** `com0com`
- **macOS/Linux:** `socat` PTY pairs

Install `socat` if you want to use **Run Simulation** without physical hardware:

```bash
# macOS
brew install socat

# Ubuntu/Debian
sudo apt install socat
```

## File Structure

- The main structure of the app is used in the file `main.py`, which is in the root directory.
- The app is currently split up into multiple directories:

```bash
  Mouser/
│
├── main.py                  # Main application entry point
├── experiment_pages/        # Pages for creating and managing lab experiments
├── databases/               # SQLite databases for users and experiments
├── shared/                  # Shared UI and utility components (e.g., tk_models.py)
├── images/ and sounds/      # External assets for UI feedback
└── requirements.txt         # Python dependencies
```

- Multiple `.gitignore` files are spread throughout the application, mostly to prevent the `__pycache__` directory and certain databases from being pushed to git.

## Contributing to Mouser

We welcome contributions from students, researchers, and developers who are passionate about open-source lab software!

#### To get started:

1. Read our [Contributing Guidelines](./ContributingGuidelines.md).
2. Check the [Issues](https://github.com/oss-slu/Mouser/issues) tab for open tasks
3. Look for labels like “good first issue” or “help wanted”
4. Fork the repo, make changes, and submit a Pull Request


## Running Executables (Windows & Linux)

In addition to running the source code locally, Mouser is also distributed as standalone executables created using **PyInstaller**.  
These executables include all dependencies and do not require Python to be installed on your computer.

### Windows
1. **Download** the latest `Mouser_Windows.exe` from the project’s GitHub Releases page.  
2. **Run the file directly** — no installation required.  
   - If Windows Defender SmartScreen appears, select **“More info → Run anyway.”**
3. The Mouser application window will launch immediately.  
4. (Optional) To rebuild the Windows executable locally:
   ```bash
   pip install -r requirements.txt
   pyinstaller --noconfirm --onefile --windowed main.py \
     --add-data "shared;shared" \
     --add-data "experiment_pages;experiment_pages" \
     --add-data "ui;ui" \
     --name "Mouser"

#### Windows RFID Testing Checklist

Use this checklist when validating RFID hardware on Windows:

1. Connect the RFID reader to your Windows laptop.
2. Confirm the reader appears in **Device Manager** and note its `COM` port (for example, `COM5`).
3. Start Mouser.
4. Open **Settings → Serial Port**.
5. Select or create a serial configuration matching your reader settings (baud/parity/data bits/stop bits).
6. Set that configuration as **RFID Reader**.
7. Open **Settings → Test Serials**.
8. Click **Test RFID** in the **RFID Readers** card.
9. Scan a tag/card.
10. Verify status changes from `Listening...` to received RFID data.

If status shows `No data received`, re-check the selected `COM` port and serial settings.

## Linux 
1. Download the latest Mouser_Linux build from the project’s GitHub Releases page (if available).
   Grant execution permission to the file so it can run:
   chmod +x Mouser_Linux
2. Run the application:
./Mouser_Linux
3. If you see display-related errors (e.g., Tk not found), install the Tk GUI library:
sudo apt install python3-tk
4. Optional: Build locally from source
    If you want to generate the Linux executable yourself, run these commands inside your project folder:
    sudo apt update
    sudo apt install python3 python3-pip python3-tk -y
    pip install -r requirements.txt
    pyinstaller --noconfirm --onefile --windowed main.py \
      --add-data "shared:shared" \
      --add-data "experiment_pages:experiment_pages" \
      --add-data "ui:ui" \
      --collect-all customtkinter \
      --hidden-import darkdetect \
      --name "Mouser"
  After the build finishes, your executable will appear at:
    dist/Mouser
    Run it with:
    ./dist/Mouser
