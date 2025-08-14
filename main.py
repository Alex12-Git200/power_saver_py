
import psutil
import os
import logging
from time import sleep
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

command_str = None
last_command_str = None

battery = psutil.sensors_battery()

if battery is None:
    logging.error("No battery found.")
    exit(1)

while True:

    battery = psutil.sensors_battery()
    percent = battery.percent
    secs_left = battery.secsleft
    is_plugged = battery.power_plugged

    if is_plugged:
        command_str = "balanced"
    if is_plugged and percent >= 50:
        command_str = "performance"
    if not is_plugged and percent <= 35:
        command_str = "power-saver"
    if not is_plugged and percent >= 35:
        command_str = "balanced"
    if not is_plugged and percent >= 90:
        command_str = "performance"

    current_profile = subprocess.check_output("powerprofilesctl get", shell = True, text = True).strip()

    if command_str != last_command_str or current_profile != command_str:
        logging.info(f"Setting mode to {command_str}")
        os.system(f"powerprofilesctl set {command_str}")
        last_command_str = command_str

    sleep(5)