#!/usr/bin/env python3

import psutil
import os
import logging
from time import sleep
import subprocess
import getpass
from pathlib import Path

# Get the actual user even when running as root
ACTUAL_USER = os.environ.get('SUDO_USER') or os.environ.get('USER') or getpass.getuser()
CONFIG_FOLDER = f"/home/{ACTUAL_USER}/.config/battery_manager"
GAMES_FILE = f"{CONFIG_FOLDER}/games.txt"

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

command_str = None
last_command_str = None
last_gaming_state = None

# Check battery exists
battery = psutil.sensors_battery()
if battery is None:
    logging.error("No battery found.")
    exit(1)

def is_gaming_func():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER, exist_ok=True)
        # Set proper ownership for the user
        import pwd
        user_info = pwd.getpwnam(ACTUAL_USER)
        os.chown(CONFIG_FOLDER, user_info.pw_uid, user_info.pw_gid)
    
    if not os.path.exists(GAMES_FILE):
        Path(GAMES_FILE).touch(exist_ok=True)
        # Set proper ownership for the user
        import pwd
        user_info = pwd.getpwnam(ACTUAL_USER)
        os.chown(GAMES_FILE, user_info.pw_uid, user_info.pw_gid)
    
    try:
        with open(GAMES_FILE) as f:
            games = set(line.strip().lower() for line in f if line.strip() and not line.strip().startswith('#'))
    except Exception as e:
        logging.error(f"Error reading games file: {e}")
        return False
    
    if not games:
        return False
    
    running_games = []
    
    # Use process_iter with additional attributes to get all processes
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username']):
        try:
            proc_info = proc.info
            if proc_info['username'] is None:
                continue
                
            proc_name = proc_info['name'].lower()
            
            # Check if any game name matches the process name
            for game in games:
                if game in proc_name:
                    running_games.append(proc_info['name'])
                    logging.debug(f"Found gaming process: {proc_info['name']} (user: {proc_info['username']})")
                    break
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return len(running_games) > 0

def determine_power_profile(percent, is_plugged, is_gaming):
    """Determine the appropriate power profile based on conditions"""
    
    # Gaming scenarios
    if is_gaming:
        if is_plugged:
            if percent >= 20:
                return "performance"
            else:  # <= 19
                return "balanced"
        else:  # not plugged
            if percent >= 60:
                return "performance"
            elif percent >= 11:  # 11-59
                return "balanced"
            else:  # <= 10
                return "power-saver"
    
    # Non-gaming scenarios
    else:
        if is_plugged:
            if percent >= 50:
                return "performance"
            else:  # < 50
                return "balanced"
        else:  # not plugged
            if percent <= 34:
                return "power-saver"
            else:  # >= 35
                return "balanced"

def get_current_profile():
    """Get current power profile with error handling"""
    try:
        result = subprocess.run(
            ["powerprofilesctl", "get"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting current profile: {e}")
        return None
    except FileNotFoundError:
        logging.error("powerprofilesctl command not found")
        return None

def set_power_profile(profile):
    """Set power profile with error handling"""
    try:
        subprocess.run(
            ["powerprofilesctl", "set", profile], 
            check=True,
            capture_output=True
        )
        logging.info(f"Successfully set power profile to: {profile}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting power profile to {profile}: {e}")
        return False
    except FileNotFoundError:
        logging.error("powerprofilesctl command not found")
        return False

# Main loop
logging.info("Starting battery manager...")

while True:
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            logging.error("Battery not found, exiting...")
            break
            
        percent = battery.percent
        is_plugged = battery.power_plugged
        is_gaming = is_gaming_func()
        
        # Log gaming state changes
        if is_gaming != last_gaming_state:
            logging.info(f"Gaming state changed: {last_gaming_state} -> {is_gaming}")
            last_gaming_state = is_gaming
        
        # Determine what profile we should use
        target_profile = determine_power_profile(percent, is_plugged, is_gaming)
        
        # Get current profile
        current_profile = get_current_profile()
        
        print(f"Battery: {percent}%, Plugged: {is_plugged}, Gaming: {is_gaming}")
        print(f"Current Profile: {current_profile}, Target: {target_profile}")
        
        # Only change if needed
        should_change = (
            target_profile != last_command_str or  # Our target changed
            (current_profile and current_profile != target_profile)  # System profile differs from target
        )
        
        if should_change:
            logging.info(f"Changing power profile from {current_profile} to {target_profile}")
            logging.info(f"Conditions: Battery={percent}%, Plugged={is_plugged}, Gaming={is_gaming}")
            
            if set_power_profile(target_profile):
                last_command_str = target_profile
        
        sleep(5)
        
    except KeyboardInterrupt:
        logging.info("Received interrupt signal, exiting...")
        break
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {e}")
        sleep(5)  # Wait before retrying

logging.info("Battery manager stopped.")