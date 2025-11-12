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
