import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

DEFAULT_QTY_SETTINGS = {
    'overhead_percent': 10,
    'categories': {
        'Resistors': {
            'enabled': True,
            'step': 50,
            'max_qty': 1000,
            'max_budget': 25.0,
        },
        'Capacitors': {
            'enabled': True,
            'step': 5,
            'max_qty': 1000,
            'max_budget': 25.0,
        },
        'Ferrite Beads': {
            'enabled': True,
            'step': 5,
            'max_qty': 1000,
            'max_budget': 25.0,
        },
        'Inductors': {
            'enabled': True,
            'step': 5,
            'max_qty': 1000,
            'max_budget': 25.0,
        },
    }
}


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
            'qty_settings': data.get('qty_settings', DEFAULT_QTY_SETTINGS),
        }
    return {'digikey_client_id': '', 'digikey_client_secret': '',
            'mouser_api_key': '', 'newark_api_key': '',
            'qty_settings': DEFAULT_QTY_SETTINGS}


def save_config(client_id='', client_secret='', mouser_api_key='',
                newark_api_key='', qty_settings=None, path=None):
    path = path or CONFIG_FILE
    existing = load_config(path)
    with open(path, 'w') as f:
        json.dump({
            'digikey_client_id': client_id or existing.get('digikey_client_id', ''),
            'digikey_client_secret': client_secret or existing.get('digikey_client_secret', ''),
            'mouser_api_key': mouser_api_key or existing.get('mouser_api_key', ''),
            'newark_api_key': newark_api_key or existing.get('newark_api_key', ''),
            'qty_settings': qty_settings or existing.get('qty_settings', DEFAULT_QTY_SETTINGS),
        }, f, indent=4)
