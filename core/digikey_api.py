import requests
import time
import urllib.parse
from typing import Dict, Optional, Callable


class DigiKeyAPI:
    """DigiKey API wrapper - API v4"""

    def __init__(self, client_id: str, client_secret: str,
                 log_callback: Callable[[str], None] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.digikey.com"
        self.access_token = None
        self.request_count = 0
        self._log = log_callback or print

    def authenticate(self):
        auth_url = "https://api.digikey.com/v1/oauth2/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.post(auth_url, data=data, headers=headers, timeout=10)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return True
            else:
                self._log(f"  Auth failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self._log(f"  Auth error: {e}")
            return False

    def search_part(self, part_number: str, retry_count: int = 3) -> Optional[Dict]:
        if not self.access_token:
            if not self.authenticate():
                return None

        url = f"{self.base_url}/products/v4/search/keyword"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-DIGIKEY-Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }
        payload = {'Keywords': part_number, 'Limit': 10, 'Offset': 0}

        for attempt in range(retry_count):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                self.request_count += 1
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    if self.authenticate():
                        continue
                    return None
                elif response.status_code == 429:
                    self._log("  Rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    return None
            except Exception:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        return None

    def get_product_pricing(self, digikey_part_number: str, retry_count: int = 3) -> Optional[Dict]:
        if not self.access_token:
            if not self.authenticate():
                return None

        encoded_pn = urllib.parse.quote(digikey_part_number, safe='')
        url = f"{self.base_url}/products/v4/search/{encoded_pn}/productdetails"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-DIGIKEY-Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }

        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                self.request_count += 1
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    if self.authenticate():
                        continue
                    return None
                elif response.status_code == 429:
                    self._log("  Rate limited on pricing API. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    return None
            except Exception:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        return None
