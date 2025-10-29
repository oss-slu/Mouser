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

### Creating Releases

Mouser uses automated GitHub Actions to build and publish releases for Windows, macOS, and Linux.

#### Creating a New Release

1. **Use the release helper script:**
   ```bash
   python scripts/create_release.py 1.2.0 --message "Added new features"
   ```

2. **Follow the printed instructions** to commit and push the tag:
   ```bash
   git add version.py
   git commit -m "Bump version to 1.2.0"
   git tag -a v1.2.0 -m "Added new features"
   git push origin v1.2.0
   ```

3. **GitHub Actions will automatically:**
   - Build executables for Windows, macOS, and Linux
   - Create a GitHub Release with all platform-specific downloads
   - Publish the release at `https://github.com/oss-slu/Mouser/releases`

#### Manual Release Process

If you prefer not to use the script:

1. **Update the version in `version.py`:**
   ```python
   __version__ = "1.2.0"
   ```

2. **Commit the version change:**
   ```bash
   git add version.py
   git commit -m "Bump version to 1.2.0"
   ```

3. **Create and push a version tag:**
   ```bash
   git tag -a v1.2.0 -m "Release message"
   git push origin v1.2.0
   ```

4. **GitHub Actions workflow** (`.github/workflows/release.yml`) will trigger automatically.

#### Release Artifacts

Each release includes:
- `Mouser_windows.zip` - Windows executable
- `Mouser_macos.zip` - macOS executable  
- `Mouser_linux.zip` - Linux executable

### Auto-Update Feature

Mouser includes built-in auto-update functionality that automatically checks for new releases from GitHub.

#### For Users

**Automatic Updates:**
- By default, automatic updates are **disabled** to give users full control
- Users can enable auto-update in the settings for automatic installation
- When enabled, Mouser will check for updates on startup
- If an update is available, it will automatically download and install
- The application will restart with the new version

**Configuring Auto-Update:**
1. Go to `Settings → Preferences` in the menu
2. In the Auto-Update Settings section:
   - **Enable automatic updates:** Turn auto-update on/off (disabled by default)
   - **Automatically download updates:** Download updates in background
   - **Automatically install updates and restart:** Install and restart automatically
3. Changes are saved immediately

**Manual Update:**
If you disable auto-update, you can manually download updates from:
`https://github.com/oss-slu/Mouser/releases`

#### For Developers

**How Auto-Update Works:**

1. **Version Detection:**
   - Current version is read from `version.py`
   - Platform is detected using `shared/platform_utils.py`

2. **Update Check:**
   - Queries GitHub API: `https://api.github.com/repos/oss-slu/Mouser/releases/latest`
   - Compares latest release version with current version

3. **Download:**
   - Downloads platform-specific zip file (`Mouser_windows.zip`, etc.)
   - Extracts to temporary directory

4. **Installation:**
   - Creates launcher script to replace running executable
   - Launches script and exits current instance
   - Launcher replaces old executable with new one
   - Restarts Mouser with updated version

**Testing Auto-Update:**

```python
# Test platform detection
python -c "from shared.platform_utils import get_platform_info; import json; print(json.dumps(get_platform_info(), indent=2))"

# Test version comparison
from packaging import version
version.parse("1.2.0") > version.parse("1.0.0")  # True
```

**Platform-Specific Details:**

| Platform | Executable Name | Download File | Update Method |
|----------|----------------|---------------|---------------|
| Windows  | `Mouser.exe`   | `Mouser_windows.zip` | Batch script launcher |
| macOS    | `Mouser`       | `Mouser_macos.zip` | Shell script launcher |
| Linux    | `Mouser`       | `Mouser_linux.zip` | Shell script launcher |

