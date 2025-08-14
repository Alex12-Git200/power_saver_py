import psutil
import os
from time import sleep

command_str = None
last_command_str = None

battery = psutil.sensors_battery()

if battery is None:
    print("No battery found.")
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


    if command_str != last_command_str:
        print(f"Setting mode to {command_str}")
        os.system(f"powerprofilesctl set {command_str}")
        last_command_str = command_str

    sleep(10)