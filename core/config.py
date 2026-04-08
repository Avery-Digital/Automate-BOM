import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config(path=None):
    path = path or CONFIG_FILE
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return {
            'digikey_client_id': data.get('digikey_client_id', ''),
            'digikey_client_secret': data.get('digikey_client_secret', ''),
        }
    return {'digikey_client_id': '', 'digikey_client_secret': ''}


def save_config(client_id, client_secret, path=None):
    path = path or CONFIG_FILE
    with open(path, 'w') as f:
        json.dump({
            'digikey_client_id': client_id,
            'digikey_client_secret': client_secret,
        }, f, indent=4)
