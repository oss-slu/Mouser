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

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
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