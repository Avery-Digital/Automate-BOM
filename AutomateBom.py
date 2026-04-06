"""
Parts Query Script for DigiKey and Mouser - FIXED VERSION
==========================================================

Fixed to use DigiKey API v4 (correct 2024+ endpoints)

Requirements:
    pip install requests beautifulsoup4 --break-system-packages
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
from urllib.parse import quote


class DigiKeyAPI:
    """
    DigiKey API wrapper - UPDATED FOR API v4
    Requires API credentials from https://developer.digikey.com/
    """
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.digikey.com"
        self.access_token = None
        
    def authenticate(self):
        """Get OAuth2 access token"""
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
                print("✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def search_part(self, part_number: str) -> Optional[Dict]:
        """Search for a part by part number using API v4"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        # CORRECTED: Use v4 endpoint
        url = f"{self.base_url}/products/v4/search/keyword"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-DIGIKEY-Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }
        
        # CORRECTED: v4 uses 'Limit' and 'Offset' instead of 'RecordCount'
        payload = {
            'Keywords': part_number,
            'Limit': 10,
            'Offset': 0
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Search successful for: {part_number}")
                return response.json()
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"URL: {url}")
                print(f"Response: {response.text[:500]}")
                return None
        except Exception as e:
            print(f"❌ Search error: {e}")
            return None
    
    def get_part_details(self, digikey_part_number: str) -> Optional[Dict]:
        """Get detailed information about a specific part"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        # CORRECTED: Use v4 endpoint  
        url = f"{self.base_url}/products/v4/search/{digikey_part_number}/productdetails"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-DIGIKEY-Client-Id': self.client_id
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Part details fetch failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Part details error: {e}")
            return None


class MouserAPI:
    """
    Mouser API wrapper
    Requires API key from https://www.mouser.com/api-hub/
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mouser.com/api/v1"
    
    def search_part(self, part_number: str) -> Optional[Dict]:
        """Search for a part by part number"""
        url = f"{self.base_url}/search/partnumber"
        
        params = {
            'apiKey': self.api_key
        }
        
        payload = {
            'SearchByPartRequest': {
                'mouserPartNumber': part_number
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Mouser search successful for: {part_number}")
                return response.json()
            else:
                print(f"❌ Mouser search failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
        except Exception as e:
            print(f"❌ Mouser search error: {e}")
            return None
    
    def search_keyword(self, keyword: str, records: int = 10) -> Optional[Dict]:
        """Search by keyword"""
        url = f"{self.base_url}/search/keyword"
        
        params = {
            'apiKey': self.api_key
        }
        
        payload = {
            'SearchByKeywordRequest': {
                'keyword': keyword,
                'records': records,
                'startingRecord': 0
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Keyword search failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Keyword search error: {e}")
            return None


# ========== USAGE EXAMPLE ==========

def example_with_api():
    """Example using official APIs with your credentials"""
    
    # DigiKey API example
    print("="*60)
    print("DigiKey API Search")
    print("="*60)
    digikey_client_id = "ENciL4CxjO0MAfsCMveTtNb2Ke96Xi5vSt5vanaouZIQbTq5"
    digikey_client_secret = "gGRJn44v69tnXdYUUEM27ELExG64yG4LoyQdVKegJlpDHTvDbXU87cevg6HvHIoo"
    
    dk = DigiKeyAPI(digikey_client_id, digikey_client_secret)
    result = dk.search_part("RC0402JR-070RL")  
    
    if result:
        print("\n✅ RESULT:")
        print(json.dumps(result, indent=2))
    else:
        print("\n❌ No results returned")


if __name__ == "__main__":
    example_with_api()