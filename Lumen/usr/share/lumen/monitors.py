import subprocess

class Monitor:

    def __init__(self, name, active=True, alias=None, software_brightness=100, hardware_brightness=100):
        self.name = name
        self.active = active
        self.alias = alias or name
        self.software_brightness = software_brightness
        self.hardware_brightness = hardware_brightness

    def display_name(self):
        return self.alias if self.alias else self.name

def get_monitors():
    monitors = []
    
    try:
        result = subprocess.run(
            ["xrandr", "--query"],
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        print("[ERROR] Xrandr call error")
        return monitors
    

    lines = result.stdout.splitlines()
    for line in lines:
        if " connected" in line or " disconnected" in line:
            parts = line.split()
            name = parts[0]
            active = "connected" in line and "disconnected" not in line
            monitors.append(Monitor(name, active))
    return monitors











