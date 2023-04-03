# Mouser

## Description

This project is meant to be used for tracking the data of animal experiments.

## Developer Guide

### Machine Requirements

- This project requires a Python 3 installation, ideally 3.9 or newer.

- Additional Python libraries also required and are found in the requirements.txt file. They can be installed using `pip install <LIBRARY>` (replace `<LIBRARY>` with the library that you want to install).

- This project works best on Windows machines, but can still be run on MacOS and Linux. The main issues with the latter concern graphics and how the app looks, but there are also some minor problems that can occur when using different operating systems.

### File Structure

- The app is currently split up into multiple folders:
  - Experiment Pages (experiment_pages)
    - This folder include files that allow for the creation and modification of lab experiments
    - Each page of the app exist in separate files. So, the code associated with the experiments menu, the experiment creation form, the data collection page, etc. are split up into different files.
    - Most of the code revolves around the user interface, but there are also sections that connect the UI to our databases
