analog force curve app

to do: beep

# Actuation Force Curve Editor Installation Guide

## Overview
The Actuation Force Curve Editor is a tool designed to create and edit the actuation force curve for analog hall effect keyboards. This guide will help you install and run the application on your PC.

## Requirements
- A PC running Windows, macOS, or Linux.
- Internet connection to download the software.

## Installation Steps

### For Windows:
1. Download the latest Python installer for Windows from the official [Python website](https://www.python.org/downloads/windows/).
   - Make sure to download a version that includes `tkinter`, which is usually included by default.
2. Run the downloaded installer.
   - **Important:** Check the box that says "Add Python to PATH" before you click "Install Now".
3. Wait for the installation to complete and then close the installer.
4. Download the Actuation Force Curve Editor software from the provided link (Note: the link to the software will be provided by the software distributor).
5. Extract the downloaded software to a folder of your choice.

### For macOS and Linux:
1. Python is typically pre-installed on macOS and most Linux distributions. If it's not installed or you want a newer version, you can download it from the official [Python website](https://www.python.org/downloads/).
2. Install `pip`, Python's package installer, by running this command in the terminal:

```sudo easy_install pip```

3. Use `pip` to install `matplotlib` and `scipy`, which are required for the application to run:

```pip install matplotlib scipy```

4. Download the Actuation Force Curve Editor software from the provided link.
5. Extract the downloaded software to a folder of your choice.

## Running the Application
1. Open a command prompt (Windows) or terminal (macOS/Linux).
2. Navigate to the folder where you extracted the Actuation Force Curve Editor software.
- You can use the `cd` command followed by the path to the folder.
3. Run the application by typing:

```python main.py```

- Replace `main.py` with the actual name of the Python script if it's different.
4. The Actuation Force Curve Editor window should now open, and you can start using the application.

## Using the Application
- Click and drag the control points on the graph to adjust the curve.
- Click "Print Curve" to print the C representation of the piecewise linear function to the console.

## Troubleshooting
If you encounter issues, make sure that:
- Python is correctly installed and added to PATH.
- You have installed all required Python packages (`matplotlib` and `scipy`).
- You are in the correct directory in the command prompt or terminal before running the application.

If you need further assistance, please contact the software support team.
