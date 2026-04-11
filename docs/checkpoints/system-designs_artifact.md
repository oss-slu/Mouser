# Checkpoint Artifact (Choice): **System Designs** — Mouser

**Project:** Mouser  
**Checkpoint Catalog Item:** System Designs  
**Artifact Type:** Markdown document (fixed-format)  
**Date:** 2026-04-10  

## Artifact identification + rationale

This artifact fulfills the **System Designs** checkpoint by documenting Mouser's current architecture in a single, contributor-friendly reference. Mouser spans multiple concerns (UI pages, serial/hardware integration, and SQLite-backed experiment files), and without a clear system map it is harder to onboard contributors, scope issues, and evolve the product safely.

We selected **System Designs** because it directly supports the final product and community strategy: it reduces onboarding friction, helps maintainers point newcomers to the right modules, and makes it easier to write high-quality issues ("this flow breaks between UI and DB") and plan roadmap work. This pairs naturally with contributor onboarding work by adding the missing technical overview.

---

## System overview

Mouser is a desktop application (Python + Tk/CustomTkinter) for creating/opening experiment files and collecting measurements with minimal user interaction. It integrates with:

- **UI layer:** CustomTkinter pages and dialogs
- **Hardware I/O:** serial ports (RFID readers, balances/calipers), with HID keyboard-wedge fallback in some flows
- **Storage:** SQLite experiment databases saved as `.mouser` (plain) or `.pmouser` (encrypted) files

---

## Repository/module architecture (static view)

### Major folders and responsibilities

- `main.py` — application entry point: creates the root window, sets geometry, initializes shared state, and starts `mainloop()`.
- `ui/` — top-level UI scaffolding (root window factory, menu bar, welcome screen) and centralized UI command callbacks.
- `experiment_pages/` — the primary application pages for experiment creation, configuration, collection, and analysis.
- `shared/` — shared utilities and cross-cutting concerns (serial, audio, resource loading, UI helpers/models).
- `databases/` — SQLite access layer and controllers for reading/writing experiment data.
- `settings/` — serial port configuration files used by the serial port controller and settings UI.

### High-level component diagram

```mermaid
flowchart LR
  A["main.py\nApp entry"] --> B["ui/root_window.py\ncreate_root_window()"]
  A --> C["ui/welcome_screen.py\nsetup_welcome_screen()"]
  A --> D["ui/menu_bar.py\nbuild_menu()"]

  D --> E["ui/commands.py\nopen/create/save/test"]
  C --> E

  E --> F["experiment_pages/*\nUI pages"]
  F --> G["databases/*\nSQLite access"]
  F --> H["shared/*\nSerial + audio + UI utils"]

  H --> I["settings/serial ports/*\nport configs"]
  G --> J[".mouser/.pmouser\nSQLite files"]
```

---

## Runtime flows (dynamic view)

### 1) Application startup

```mermaid
sequenceDiagram
  participant User
  participant Main as main.py
  participant Root as ui/root_window.py
  participant Welcome as ui/welcome_screen.py
  participant Menu as ui/menu_bar.py

  User->>Main: Launch app (python main.py)
  Main->>Root: create_root_window()
  Main->>Welcome: setup_welcome_screen(root, main_frame)
  Main->>Menu: build_menu(root, experiments_frame, SerialPortController("reader"))
  Main-->>User: UI visible + ready
```

---

### 2) Experiment file lifecycle (open/create/save)

#### Open existing experiment (`.mouser` or `.pmouser`)

```mermaid
sequenceDiagram
  participant UI as Welcome/Menu UI
  participant Cmd as ui/commands.py
  participant FU as shared/file_utils.py
  participant DB as databases/experiment_database.py
  participant Page as experiment_pages/* UI

  UI->>Cmd: open_file()
  Cmd->>FU: create_temp_copy() OR create_temp_from_encrypted()
  Cmd->>DB: ExperimentDatabase(temp_path)
  Cmd->>Page: ExperimentMenuUI(root, temp_path, experiments_frame)
```

**Key design choice:** the app works on a **temporary copy** of the experiment DB file during runtime. "Save" writes the temp DB back to the original `.mouser` path or re-encrypts for `.pmouser`.

#### Create a new experiment

```mermaid
sequenceDiagram
  participant UI as Welcome/Menu UI
  participant Cmd as ui/commands.py
  participant New as experiment_pages/create_experiment/new_experiment_ui.py

  UI->>Cmd: create_file()
  Cmd->>New: NewExperimentUI(root, experiments_frame)
```

---

### 3) Data collection (RFID vs non-RFID)

At a high level, Mouser supports two primary "identify the animal" modes:

- **RFID mode:** the app listens for an RFID scan, then associates measurements with the scanned animal.
- **Non-RFID mode:** the app walks through animals (auto-increment) and records measurements for the current animal.

```mermaid
flowchart TD
  A["DataCollectionUI\nexperiment_pages/experiment/data_collection_ui.py"] --> B{"experiment_uses_rfid()"}
  B -- "Yes" --> C["Start Scanning\nrfid_listen()"]
  C --> D["Serial/HID input\n(shared serial modules)"]
  D --> E["Select animal by RFID\n+ confirm feedback"]
  E --> F["Capture measurement(s)\n(manual or serial device)"]
  F --> G["Write measurement(s)\nExperimentDatabase"]

  B -- "No" --> H["Start\nauto_increment()"]
  H --> I["Select next animal_id"]
  I --> F
```

---

## Data model (SQLite)

The experiment file is a SQLite database. Core tables created by `ExperimentDatabase._initialize_tables()`:

```mermaid
erDiagram
  experiment {
    TEXT name
    TEXT species
    INTEGER uses_rfid
    INTEGER num_animals
    INTEGER num_groups
    INTEGER cage_max
    INTEGER measurement_type
    TEXT id
    TEXT investigators
    TEXT measurement
  }

  animals {
    INTEGER animal_id PK
    INTEGER group_id
    TEXT rfid
    TEXT remarks
    INTEGER active
  }

  animal_measurements {
    INTEGER measurement_id
    INTEGER animal_id FK
    TEXT timestamp
    REAL value
  }

  groups {
    INTEGER group_id PK
    TEXT name
    INTEGER num_animals
    INTEGER cage_capacity
  }

  animals ||--o{ animal_measurements : "records"
  groups  ||--o{ animals : "contains"
```

---

## Extension points (for contributors)

- **UI actions:** add/route a new menu option via `ui/menu_bar.py` -> `ui/commands.py`.
- **New pages:** implement additional flows as a page under `experiment_pages/...` and use shared frame helpers from `shared/tk_models.py`.
- **Serial devices:** extend patterns in `shared/serial_port_controller.py`, `shared/serial_listener.py`, and `shared/serial_handler.py`.
- **Persistence:** extend `databases/experiment_database.py` with backward-compatible initialization for new tables/fields.

