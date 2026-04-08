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
            'mouser_api_key': data.get('mouser_api_key', ''),
            'newark_api_key': data.get('newark_api_key', ''),
        }
    return {'digikey_client_id': '', 'digikey_client_secret': '',
            'mouser_api_key': '', 'newark_api_key': ''}


def save_config(client_id='', client_secret='', mouser_api_key='',
                newark_api_key='', path=None):
    path = path or CONFIG_FILE
    existing = load_config(path)
    with open(path, 'w') as f:
        json.dump({
            'digikey_client_id': client_id or existing.get('digikey_client_id', ''),
            'digikey_client_secret': client_secret or existing.get('digikey_client_secret', ''),
            'mouser_api_key': mouser_api_key or existing.get('mouser_api_key', ''),
            'newark_api_key': newark_api_key or existing.get('newark_api_key', ''),
        }, f, indent=4)
