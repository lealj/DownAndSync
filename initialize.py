import json
from platformdirs import user_data_dir
import os

APP_NAME = "DownAndSync"
CONFIG_FILE = os.path.join(user_data_dir(APP_NAME), "config.json")
DEFAULT_CONFIG = {
    "directory_path": ""
}

def ensure_config_directory():
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)


def initialize_config():
    ensure_config_directory()
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)
        print(f"Default config.json created at {CONFIG_FILE}")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}


def get_directory_path():
    config = load_config()
    directory_path = config.get("directory_path", "")
    return directory_path


def save_config(data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Config saved to {CONFIG_FILE}")


def get_directory_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        
        return config.get("directory_path", "")
    else:
        print("Config file not found")
        return ""