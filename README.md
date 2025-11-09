# Mouser

## Description

This software is used for collecting and analyzing data from animal experiments. While in the lab, scientists are often required to keep their environments very clean, which means that they must limit how much they touch the computers and lab equipment. To facilitate this, Mouser allows laboratory equipment (balances, calipers, RFID chip readers) to be connected to a PC, and researchers can quickly take repeated measurements with as little interaction as possible. Running as a desktop app, users of the software can create and manage experiments in one easy place. Animals implanted with RFID biochips can be scanned into the system for easy identification and data access. Once a session is started, the user is able to take measurements of the animals using devices connected to the computer without having to use the keyboard or the mouse. The program gives confirmation to the user through sounds and changes in display, allowing them to focus on the experiment.

## Developer Guide

### Machine Requirements

- This project requires a Python 3 installation, ideally 3.9 or newer.

- Additional Python libraries also required are found in the `requirements.txt` file. They can be installed using `pip install -r requirements.txt`.

- This project works best on Windows machines, but can still be run on MacOS and Linux. The main issues with the latter concern graphics and how the app looks, but there are also some minor problems that can occur when using different operating systems.

### Local Development Environment

- Clone the repository to your local machine.
- Install the required libraries and modules.
- In the root directory, run `python main.py` to run the program locally.

### File Structure

- The main structure of the app is used in the file `main.py`, which is in the root directory.
- The app is currently split up into multiple directories:
  - Experiment Pages (`experiment_pages`)
    - This directory include files that allow for the creation and modification of lab experiments
    - Each page of the app exist in separate files. So, the code associated with the experiments menu, the experiment creation form, the data collection page, etc. are split up into different files.
    - Most of the code revolves around the user interface, but there are also sections that grab data from or send data to the databases
  - Databases (`databases`)
    - This directory is where all of the databases are stored, including the experiments and users databases.
    - The databases are managed using SQLite.
- There are two files in the `shared` directory, `tk_models.py` and `scrollable_frame.py`, that are shared across many of the files in this app. They both include classes that are used for the majority of the app, so the design can be easily changed if necessary. This directory also contains external assets in `images` and `sounds` folders.
- Multiple `.gitignore` files are spread throughout the application, mostly to prevent the `__pycache__` directory and certain databases from being pushed to git.

### Contribution Guide

To contribute to this project, create a pull request and link the related issue. If you are creating a new issue follow the templates located in the `.github` folder.


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