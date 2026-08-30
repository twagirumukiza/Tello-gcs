"""Détection du réseau Wi-Fi du Tello avant tentative de connexion.

Voir chapitre 2 du livre.
"""
import platform
import re
import subprocess


def detect_tello_network() -> str | None:
    system = platform.system()

    if system == "Windows":
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True
        )
        match = re.search(r"SSID\s*:\s*(TELLO-\S+)", result.stdout)
        return match.group(1) if match else None

    if system == "Darwin":
        result = subprocess.run(
            ["networksetup", "-getairportnetwork", "en0"], capture_output=True, text=True
        )
        match = re.search(r"Current Wi-Fi Network:\s*(TELLO-\S+)", result.stdout)
        return match.group(1) if match else None

    # Linux
    result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
    ssid = result.stdout.strip()
    return ssid if ssid.startswith("TELLO-") else None
