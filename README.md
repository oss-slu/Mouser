# Mouser

## Description

This project is meant to be used for used for collecting and analyzing data from animal experiments. 
Mouser allows laboratory equipment (balances, calipers, RFID chip readers) to be connected to a PC, and researchers can quickly take repeated measurements with as little interaction as possible. 
The program gives confirmation to the user through sounds and changes in display, allowing them to focus on the experiment.

## Developer Guide

### Machine Requirements

- This project requires a Python 3 installation, ideally 3.9 or newer.

- Additional Python libraries also required and are found in the `requirements.txt` file. They can be installed using `pip install -r requirements.txt` 
All the Libraries 
  - Licenses for these libraries: https://docs.google.com/spreadsheets/d/10V4Tzy8WnGbYQM76NdHAqNodl70Ce8RNN2XIa36jQHw/edit#gid=0

- This project works best on Windows machines, but can still be run on MacOS and Linux. The main issues with the latter concern graphics and how the app looks, but there are also some minor problems that can occur when using different operating systems.

### File Structure

- The main structure of the app is used in the file `main.py`, which is in the root directory.
- The app is currently split up into multiple directories:
  - Experiment Pages (`experiment_pages`)
    - This directory include files that allow for the creation and modification of lab experiments
    - Each page of the app exist in separate files. So, the code associated with the experiments menu, the experiment creation form, the data collection page, etc. are split up into different files.
    - Most of the code revolves around the user interface, but there are also sections that grab data from or send data to the databases
  - images
    - This directory includes all the images utilized in the project
  - sounds
    - This directory includes sounds utilized in the project
  - Database APIs (`database_apis`)
    - This directory has the code that is essentially a "buffer" between the front end of the application and the databases.
    - There are two Python files in the directory: one works with the database of users, and the other works with the database of experiments.
      - Both have methods to connect to our SQLite databases, where they can be created, modified, and examined.
  - Databases (`databases`)
    - This directory is where all of the databases are stored, including the experiments and users databases.
    - The databases are managed using SQLite.
- The code that handles the account/login management is spread throughout the root directory. The two files for this are `accounts.py` and `login.py`. (In the future, they may end up in their own directory, but they are in the root at the moment.)
- There are two files in the root directory, `tk_models.py` and `scrollable_frame.py`, that are shared across many of the files in this app. They both include classes that are used for the majority of the app, so the design can be easily changed if necessary. (Again, these may have a different directory later on.)
- External assets are either put into the `images` directory, or the `sounds` directory.
  - It should be determined whether we have permission to use any assets (current or new).
- Multiple `.gitignore` files are spread throughout the application, mostly to prevent the `__pycache__` directory and certain databases from being pushed to git.
