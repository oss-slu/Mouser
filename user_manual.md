# Mouser User Manual

## 1. Introduction

Mouser is a desktop application that aids in monitoring and gathering information of the experiment with the assistance of RFID. It enables users to scan RFID tags and match them with experiments and record the results in a local database.

The manual is simple and has step-by-step directions to ensure new users acquire knowledge on using the application effectively.

---

## 2. Getting Started

### 2.1 Launching the Application

1. Start a command prompt / OS terminal.
2. Go to the directory of Mouser project.
3. Run the application using: python main.py or python3 main.py


4. The main application window will open.

---

### 2.2 Initial Screen

In the application, the main interface is displayed when started. Here, the users are able to:

* Start or select an experiment
* Interact with RFID input.
* Check the status and results of the view system.

---

## 3. Interface Overview

Mouser interface has the following components:

* Main Window: This will show the information regarding the system and running experiments.
* Control Buttons: Buttons to be used in activation, deactivation or resetting of actions.
* Data Display Area: The RFID scanned data and experimental results are shown.
* Status Indicators: are used to give feedback on system activity and connectivity.

---

## 4. Main User Workflow

### 4.1 Launching the application

Run python main.py or python3 main.py to open the Mouser application

---

### 4.2 Select or Create an Experiment

* Select an experiment (or create a new one).
* The experiment that is selected will be displayed on the screen.

---

### 4.3 Scan RFID Tags: This step involves scanning RFID tags.

* Put an RFID tag next to the RFID reader that is connected.
* The input will be automatically detected in the system.

---

### Step 4: Data Processing

RFID scanned data is processed in the application after scanning all tags.
The system is able to track and arrange the gathered data since the scanned tags are connected to the ongoing experiment.

---

### Step 5: View Results

* Scanned data will be displayed in the display area.
* Experiment progress may be monitored in real time by the users.

---

### Step 6: Exit Mouser Application

* The data will be automatically saved in the database.
* Close application to exit.

---

## 5. Key Features

### 5.1 RFID Scanning

* Automatically recognizes the RFID tag.
* Scanning tags with associates of the running experiment.

---

### 5.2 Experiment Management

* Tabulates information of various experiments.
* Aids in tracking and separation of the outcomes.

---

### 5.3 Data Storage

* Stores all the obtained information to a local SQLite database.
* Guarantees data inter-session.

---

## 6. Common Actions

### Restarting the Application

* Close Mouser application
* Reopen application using python main.py or python3 main.py.

---

### Resetting an Experiment

* Clear current or existing data by resetting (where available)

---

### Viewing Stored Data

* All the data is automatically stored.
* It may be looked at using application interface or database tools.

---

## 7. Troubleshooting

### Application Not Starting

* If application does not start Ensure that you have Python installed.
* Check any necessary dependencies are in place.
* Check in terminal to verify error messages.

---

### RFID Scanner is not working.

* Check the proper connection of the device.
* Make sure that the correct serial port is being used.
* Restart the application

---

### Data Not Appearing

* Make sure that an experiment is selected.
* Check the RFID scan has been successful.

---

## 8. Notes

* This application has to be equipped with appropriate RFID hardware.
* Before starting, make sure that all components are attached.
* The program will be locally utilized.

---

## 9. Support

Development team: The development team may be contacted via the project repository or by reaching out to the development team. 
