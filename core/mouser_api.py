import requests
import time
from typing import Dict, Optional, Callable


class MouserAPI:
    """Mouser Electronics API wrapper"""

    def __init__(self, api_key: str, log_callback: Callable[[str], None] = None):
        self.api_key = api_key
        self.base_url = "https://api.mouser.com/api/v1"
        self.request_count = 0
        self._log = log_callback or print

    def search_part(self, part_number: str, retry_count: int = 3) -> Optional[Dict]:
        """Search for a part by manufacturer part number."""
        url = f"{self.base_url}/search/partnumber"
        params = {'apiKey': self.api_key}
        payload = {
            'SearchByPartRequest': {
                'mouserPartNumber': part_number,
                'partSearchOptions': ''
            }
        }
        headers = {'Content-Type': 'application/json'}

        for attempt in range(retry_count):
            try:
                response = requests.post(url, params=params, json=payload,
                                         headers=headers, timeout=15)
                self.request_count += 1

                if response.status_code == 200:
                    data = response.json()
                    errors = data.get('Errors', [])
                    if errors:
                        for err in errors:
                            self._log(f"  Mouser API error: {err.get('Message', err)}")
                    return data
                elif response.status_code == 429:
                    self._log("  Mouser rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    self._log(f"  Mouser HTTP {response.status_code}")
                    return None

            except Exception as e:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                self._log(f"  Mouser error: {e}")
                return None

        return None

    def extract_product_data(self, product: Dict) -> Dict:
        """Extract relevant data from a Mouser product result."""
        # Price - get the lowest quantity price break
        unit_price = 0
        raw_breaks = product.get('PriceBreaks', [])
        parsed_breaks = []
        if raw_breaks:
            price_str = raw_breaks[0].get('Price', '$0')
            try:
                unit_price = float(price_str.replace('$', '').replace(',', ''))
            except (ValueError, TypeError):
                unit_price = 0
            for pb in raw_breaks:
                try:
                    parsed_breaks.append({
                        'quantity': pb.get('Quantity', 0),
                        'unit_price': float(pb.get('Price', '$0').replace('$', '').replace(',', '')),
                    })
                except (ValueError, TypeError):
                    pass

        # Availability - use AvailabilityInStock (actual stock, not on-order)
        avail_str = product.get('AvailabilityInStock', '0') or '0'
        available = 0
        try:
            avail_clean = str(avail_str).replace(',', '')
            available = int(avail_clean)
        except (ValueError, TypeError, IndexError):
            available = 0

        # Description
        description = product.get('Description', '')

        # Mouser P/N
        mouser_pn = product.get('MouserPartNumber', '')

        # Manufacturer
        manufacturer = product.get('Manufacturer', '')

        # Product URL
        product_url = product.get('ProductDetailUrl', '')

        # Datasheet
        datasheet_url = product.get('DataSheetUrl', '')

        return {
            'description': description,
            'dist_pn': mouser_pn,
            'product_url': product_url,
            'available': available,
            'price': unit_price,
            'temperature': '',
            'footprint': '',
            'component_value': '',
            'price_breaks': parsed_breaks,
            'distributor': 'Mouser',
            'manufacturer': manufacturer,
        }

    @staticmethod
    def _normalize_pn(pn: str) -> str:
        return pn.upper().replace('-', '').replace(' ', '').replace('.', '').lstrip('0')

    def find_best_match(self, part_number: str) -> Optional[Dict]:
        """Search and return the best matching product data, or None."""
        result = self.search_part(part_number)
        if not result:
            return None

        search_results = result.get('SearchResults', {})
        parts = search_results.get('Parts', [])

        if not parts:
            return None

        norm_search = self._normalize_pn(part_number)

        # Try exact match first
        for p in parts:
            mpn = p.get('ManufacturerPartNumber', '')
            if mpn.upper() == part_number.upper():
                self._log(f"  [Mouser] Exact match: {mpn}")
                return self.extract_product_data(p)

        # Normalized match
        for p in parts:
            mpn = p.get('ManufacturerPartNumber', '')
            if self._normalize_pn(mpn) == norm_search:
                self._log(f"  [Mouser] Normalized match: {mpn}")
                return self.extract_product_data(p)

        # Partial match
        for p in parts:
            mpn = p.get('ManufacturerPartNumber', '')
            if part_number.upper() in mpn.upper() or mpn.upper() in part_number.upper():
                self._log(f"  [Mouser] Partial match: {mpn}")
                return self.extract_product_data(p)

        # Fallback to first
        first = parts[0]
        self._log(f"  [Mouser] Using first result: {first.get('ManufacturerPartNumber', 'N/A')}")
        return self.extract_product_data(first)
