import requests
import time
from typing import Dict, Optional, Callable


class NewarkAPI:
    """Newark/element14 API wrapper"""

    def __init__(self, api_key: str, log_callback: Callable[[str], None] = None):
        self.api_key = api_key
        self.base_url = "https://api.element14.com/catalog/products"
        self.request_count = 0
        self._log = log_callback or print

    def search_part(self, part_number: str, retry_count: int = 3) -> Optional[Dict]:
        """Search for a part by manufacturer part number."""
        params = {
            'term': f'manuPartNum:{part_number}',
            'storeInfo.id': 'www.newark.com',
            'resultsSettings.offset': 0,
            'resultsSettings.numberOfResults': 10,
            'resultsSettings.responseGroup': 'large',
            'callInfo.apiKey': self.api_key,
            'callInfo.responseDataFormat': 'JSON',
        }

        for attempt in range(retry_count):
            try:
                response = requests.get(self.base_url, params=params, timeout=15)
                self.request_count += 1

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    self._log("  Newark rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    self._log(f"  Newark HTTP {response.status_code}")
                    return None

            except Exception as e:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                self._log(f"  Newark error: {e}")
                return None

        return None

    def extract_product_data(self, product: Dict) -> Dict:
        """Extract relevant data from a Newark product result."""
        # Price - first price break (qty 1)
        unit_price = 0
        prices = product.get('prices', [])
        parsed_breaks = []
        if prices:
            try:
                unit_price = float(prices[0].get('cost', 0))
            except (ValueError, TypeError):
                unit_price = 0
            for pb in prices:
                try:
                    parsed_breaks.append({
                        'quantity': pb.get('from', 0),
                        'unit_price': float(pb.get('cost', 0)),
                    })
                except (ValueError, TypeError):
                    pass

        # Availability from stock.level, fallback to inv
        available = 0
        stock = product.get('stock', {})
        if isinstance(stock, dict):
            available = stock.get('level', 0)
            # Check regional breakdown for better US stock count
            regional = stock.get('regionalBreakdown', [])
            for r in regional:
                if r.get('warehouse') == 'US':
                    available = r.get('level', available)
                    break
        if available == 0:
            try:
                available = int(product.get('inv', 0))
            except (ValueError, TypeError):
                available = 0

        # Description
        description = product.get('displayName', '')

        # Newark P/N (SKU)
        newark_pn = product.get('sku', '')

        # Manufacturer
        manufacturer = product.get('brandName', '')

        # Product URL
        product_url = f"https://www.newark.com/search?st={newark_pn}" if newark_pn else ''

        # Extract component value, footprint, and temperature from attributes
        component_value = ""
        footprint = ""
        temp_min = ""
        temp_max = ""
        value_labels = ['resistance', 'inductance', 'capacitance']
        attributes = product.get('attributes', [])
        for attr in attributes:
            label = (attr.get('attributeLabel', '') or '').lower()
            val = attr.get('attributeValue', '')
            unit = attr.get('attributeUnit', '')

            # Component value
            if not component_value:
                for vl in value_labels:
                    if label == vl:
                        component_value = f"{val} {unit}".strip() if unit else val
                        break

            # Footprint / package
            if not footprint and ('case' in label or 'package' in label):
                if val and val != '-':
                    footprint = val

            # Temperature
            if 'operating temperature min' in label and val:
                temp_min = f"{val} {unit}".strip() if unit else val
            elif 'operating temperature max' in label and val:
                temp_max = f"{val} {unit}".strip() if unit else val

        temperature = ""
        if temp_min and temp_max:
            temperature = f"{temp_min} ~ {temp_max}"
        elif temp_min:
            temperature = temp_min
        elif temp_max:
            temperature = temp_max

        return {
            'description': description,
            'dist_pn': newark_pn,
            'product_url': product_url,
            'available': available,
            'price': unit_price,
            'temperature': temperature,
            'footprint': footprint,
            'component_value': component_value,
            'price_breaks': parsed_breaks,
            'distributor': 'Newark',
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

        products = []
        mfr_results = result.get('manufacturerPartNumberSearchReturn', {})
        if mfr_results:
            products = mfr_results.get('products', [])

        if not products:
            return None

        norm_search = self._normalize_pn(part_number)

        # Filter to exact MPN matches first (literal or normalized), prefer stocked cut tape
        exact_matches = []
        for p in products:
            mpn = p.get('translatedManufacturerPartNumber', '') or p.get('manufacturerPartNumber', '')
            if mpn.upper() == part_number.upper() or self._normalize_pn(mpn) == norm_search:
                exact_matches.append(p)

        # If we have exact matches, prefer stocked with inventory
        if exact_matches:
            # Sort: STOCKED with inventory first, then by unit of measure (cut tape preferred)
            for p in exact_matches:
                uom = (p.get('unitOfMeasure', '') or '').upper()
                stock_level = 0
                stock_data = p.get('stock', {})
                if isinstance(stock_data, dict):
                    stock_level = stock_data.get('level', 0)
                if stock_level == 0:
                    stock_level = int(p.get('inv', 0) or 0)
                if stock_level > 0 and 'CUT TAPE' in uom:
                    self._log(f"  [Newark] Exact match (cut tape, in stock): {p.get('sku')}")
                    return self.extract_product_data(p)

            # Fallback: any exact match with stock
            for p in exact_matches:
                stock_level = 0
                stock_data = p.get('stock', {})
                if isinstance(stock_data, dict):
                    stock_level = stock_data.get('level', 0)
                if stock_level == 0:
                    stock_level = int(p.get('inv', 0) or 0)
                if stock_level > 0:
                    self._log(f"  [Newark] Exact match (in stock): {p.get('sku')}")
                    return self.extract_product_data(p)

            # Fallback: first exact match even if no stock
            self._log(f"  [Newark] Exact match: {exact_matches[0].get('sku')}")
            return self.extract_product_data(exact_matches[0])

        # Partial match
        for p in products:
            mpn = p.get('translatedManufacturerPartNumber', '') or p.get('manufacturerPartNumber', '')
            if part_number.upper() in mpn.upper() or mpn.upper() in part_number.upper():
                self._log(f"  [Newark] Partial match: {mpn}")
                return self.extract_product_data(p)

        # Fallback to first
        self._log(f"  [Newark] Using first result: {products[0].get('sku', 'N/A')}")
        return self.extract_product_data(products[0])
