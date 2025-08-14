# Battery Controller

This is a Python script for Linux laptops that use the [power-profiles-daemon](https://gitlab.freedesktop.org/upower/power-profiles-daemon).  
Without this daemon, the script will not work.

## What It Does

- Checks if your laptop is plugged in.
- Monitors battery percentage.
- Automatically adjusts the power profile using `powerprofilesctl` based on battery status.

## Future Plans

- Add checks for fan speed, temperature, and other system metrics.
- Make the script smarter and more adaptive.

## Usage

1. Make sure `power-profiles-daemon` is installed and running.
2. Run the script with Python 3:
   ```
   python3 main.py
   ```

Currently, the script is simple (about 40 lines of code) and easy to use.