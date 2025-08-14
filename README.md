# Battery Manager

An intelligent Python script for Linux laptops that automatically manages power profiles based on battery status and gaming activity using [power-profiles-daemon](https://gitlab.freedesktop.org/upower/power-profiles-daemon).

## Features

- **Automatic Power Profile Switching**: Intelligently switches between performance, balanced, and power-saver modes
- **Gaming Detection**: Monitors running processes to detect gaming sessions and adjusts profiles accordingly  
- **Battery-Aware**: Makes decisions based on battery percentage and charging status
- **Service Integration**: Designed to run as a systemd service for continuous operation
- **User-Configurable**: Easy-to-edit games list for custom gaming detection

## How It Works

The script continuously monitors:
- Battery percentage and charging status
- Running processes to detect gaming activity
- Current power profile state

### Power Profile Logic

**Non-Gaming Mode:**
- **Plugged in + ≥50% battery**: Performance mode
- **Plugged in + <50% battery**: Balanced mode  
- **Unplugged + ≤34% battery**: Power-saver mode
- **Unplugged + ≥35% battery**: Balanced mode

**Gaming Mode:**
- **Plugged in + ≥20% battery**: Performance mode
- **Plugged in + ≤19% battery**: Balanced mode
- **Unplugged + ≥60% battery**: Performance mode
- **Unplugged + 11-59% battery**: Balanced mode
- **Unplugged + ≤10% battery**: Power-saver mode

## Prerequisites

1. **power-profiles-daemon**: Must be installed and running
   ```bash
   # Check if installed
   powerprofilesctl --help
   
   # Install on Ubuntu/Debian
   sudo apt install power-profiles-daemon
   
   # Install on Arch
   sudo pacman -S power-profiles-daemon
   
   # Enable and start the service
   sudo systemctl enable --now power-profiles-daemon
   ```

2. **Python dependencies**:
   ```bash
   pip install psutil
   ```

## Installation & Setup

### 1. Download and Setup the Script

```bash
# Clone or download the script
sudo cp battery_manager.py /usr/local/bin/
sudo chmod +x /usr/local/bin/battery_manager.py
```

### 2. Configure Gaming Detection

Create your games list (this will be created automatically on first run, but you can pre-configure it):

```bash
mkdir -p ~/.config/battery_manager
```

Edit `~/.config/battery_manager/games.txt` and add game executable names (one per line):
```
steam
wine
gamemode
lutris
minecraft
cs2
dota2
# Add your games here
# NOTE: Add you game name the same as the id, so for e.g. if you are running supertux, run this: pgrep -a -f supertux (while running the game)
# and the output is the correct name to put on games.txt
```

### 3. Set Up as a System Service

Create the systemd service file:

```bash
sudo nano /etc/systemd/system/battery-manager.service
```

Add this content:
```ini
[Unit]
Description=Battery Manager - Automatic Power Profile Controller
After=multi-user.target power-profiles-daemon.service
Wants=power-profiles-daemon.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/battery_manager.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable battery-manager.service

# Start the service immediately
sudo systemctl start battery-manager.service
```

## Service Management Commands

```bash
# Check service status
sudo systemctl status battery-manager.service

# View logs
sudo journalctl -u battery-manager.service -f

# Stop the service
sudo systemctl stop battery-manager.service

# Restart the service
sudo systemctl restart battery-manager.service

# Disable auto-start
sudo systemctl disable battery-manager.service
```

## Manual Usage

You can also run the script manually for testing:

```bash
# Run directly
sudo python3 battery_manager.py

# Or if installed in /usr/local/bin
sudo battery_manager.py
```

**Note**: Root privileges are required to monitor all user processes and change system power profiles.

## Configuration

### Games Configuration

The script reads from `~/.config/battery_manager/games.txt`. Each line should contain a process name to monitor:

- Use lowercase names
- Partial matches work (e.g., "steam" matches "steam.exe")
- Lines starting with `#` are comments
- Empty lines are ignored

### Customizing Thresholds

To modify battery thresholds or power profile logic, edit the `determine_power_profile()` function in the script.

## Troubleshooting

**Service won't start:**
- Check if power-profiles-daemon is running: `systemctl status power-profiles-daemon`
- Verify the script path in the service file
- Check logs: `sudo journalctl -u battery-manager.service`

**Gaming detection not working:**
- Ensure game names in `games.txt` match actual process names
- Check running processes: `ps aux | grep <game-name>`
- View debug logs when running manually

**Permission issues:**
- The service must run as root to monitor all processes
- Config files are automatically created with proper user permissions

## Future Plans

- Temperature and fan speed monitoring
- CPU frequency scaling integration  
- Machine learning-based usage pattern detection
- Web interface for configuration
- Multiple user profile support
- Integration with external hardware controls

## IMPORTANT

- Just found out game mode doesn't work when you run it as service, I will fix it when i have time.

## License

MIT License - Feel free to modify and distribute.
