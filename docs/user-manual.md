# Mouser User Manual (Workflow Guide)

Mouser is a desktop app for running animal experiment workflows with minimal mouse/keyboard interaction, supporting RFID-based identification and quick measurement entry.

## 1) Start Here (Quick Start)

1. Launch Mouser.
2. From the **Home** screen, choose one:
   - **New Experiment** (create a new experiment file)
   - **Open Experiment** (open an existing `.mouser` / `.pmouser` file)
3. In the **Experiment Menu**, follow the recommended order:
   1) **Group Configuration** → 2) **Cage Configuration** → 3) **Map RFID** (if enabled) → 4) **Data Collection** → 5) **Data Analysis / Export**

## 2) Home Screen Options

From the Home screen you can:

- **New Experiment**: create a new experiment and save it to a folder you choose.
- **Open Experiment**: open an existing experiment file:
  - `.mouser` = standard experiment database file
  - `.pmouser` = password-protected (encrypted) experiment database file
- **Equipment Testing**: validate connected equipment behavior (helpful before collecting real data).
- **Serial Port Testing**: configure/verify serial port connections for devices.

You can also use the menu bar:

- **File → New Experiment**
- **File → Open Experiment**
- **Info → Documentation**

## 3) Create a New Experiment (Step-by-Step)

1. Go to **File → New Experiment** (or **Home → New Experiment**).
2. Fill in the experiment details (typical fields):
   - **Experiment name** (required)
   - **Password (optional)**: if set, the file is saved as `.pmouser`
   - **Investigators**
   - **Species**
   - **Measurement item(s)** (what you plan to record)
   - **Number of animals**, **groups**, and **animals per cage**
   - **Uses RFID** (enable if you will identify animals by RFID tag scans)
3. Continue to **Group Configuration**:
   - Name the groups.
   - Choose **Input Method**:
     - **Automatic**: intended for workflows using connected devices / scanning
     - **Manual**: intended for typing measurements
4. Review the **Summary** page and click **Create**.
5. Choose a folder to save the experiment file.

## 4) Open an Existing Experiment

1. Go to **File → Open Experiment** (or **Home → Open Experiment**).
2. Select a file:
   - `.mouser`: opens directly
   - `.pmouser`: enter the password when prompted
3. Mouser opens the **Experiment Menu** for that experiment.

## 5) Experiment Menu (Your Main Hub)

The Experiment Menu is the central hub for:

- **Map RFID**: required before data collection when RFID is enabled.
- **Data Collection**: collect today’s measurements for each animal.
- **Data Analysis**: view/export data and trends.
- **Summary View**: review key experiment details.
- **Investigators**: view/update investigator list (if available in your build).
- **Group Configuration**: review/update group names and input method.
- **Cage Configuration**: assign animals to cages/groups (includes quick actions like autosort/randomize/swap/move).
- **Delete Experiment**: permanently deletes the experiment file (use with caution).

## 6) Map RFID (If RFID Is Enabled)

Use **Map RFID** to link each animal to an RFID tag **before** collecting data.

Typical workflow:

1. Open **Map RFID** from the Experiment Menu.
2. Start scanning (serial RFID reader or HID keyboard-wedge reader, depending on your setup).
3. For each animal:
   - select/confirm the target animal ID
   - scan the RFID tag
   - confirm it appears in the mapping table
4. Save/return to the Experiment Menu when finished.

If RFID is enabled, Mouser may block or warn when starting Data Collection until all expected animals have mappings.

## 7) Cage Configuration (Assign Animals)

Use **Cage Configuration** to place animals into cages/groups.

Common actions:

1. Open **Cage Configuration** from the Experiment Menu.
2. Use quick actions as needed:
   - **AutoSort**, **Randomize**, **Swap**, **Move Selected**
3. If RFID is enabled, you can scan to select animals quickly (depending on your device/input mode).
4. Save and return to the Experiment Menu.

## 8) Data Collection (Daily Measurement Flow)

Use **Data Collection** to record measurements for today’s date.

1. Open **Data Collection** from the Experiment Menu.
2. Start collection:
   - **RFID experiments**: click **Start scanning** and scan an animal tag to pull up that animal.
   - **Non-RFID experiments**: click **Start** to step through animals (auto-increment flow).
3. Enter/confirm the measurement(s) for the selected animal.
4. Watch the table **Status** update (e.g., Pending → In Progress → Done).
5. Continue until all animals are complete for today.

Saving behavior:

- Mouser commits data to the experiment database as you collect it.
- For non-encrypted experiments (`.mouser`), Mouser can also auto-save the open copy back to the original file during collection.
- For encrypted experiments (`.pmouser`), saving is handled through the password-protected save flow.

### Export CSV (from Data Collection)

The Data Collection page includes **Export CSV** for a quick export of the current experiment’s data.

## 9) Data Analysis (Export + Trends)

Use **Data Analysis** to:

- export data (for spreadsheets / stats tools)
- review measurement trends over time (when available)

Open it from the Experiment Menu and use the Export controls to save results to a location you choose.

## 10) Experiment Files and Safety Notes

- Keep experiment files in a stable folder (network drives and removable drives can be unreliable).
- `.pmouser` files require the correct password to open.
- **Delete Experiment** removes the experiment file permanently; this cannot be undone.

## 11) Troubleshooting (Quick Checks)

- **RFID not reading**
  - Try **Home → Serial Port Testing** and confirm the reader is detected/configured.
  - If using a HID keyboard-wedge RFID reader, ensure the system is receiving keystrokes from the device.
- **Can’t start data collection**
  - If RFID is enabled, open **Map RFID** and finish mapping all animals first.
- **Nothing saves**
  - Confirm you are working from an experiment file (not a temporary scratch copy).
  - For `.pmouser`, ensure you used the correct password and closed/saved normally.

