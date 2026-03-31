import requests

def get_coingecko_price(token_id="ethereum", vs_currency="usd"):
    """
    Fetch real-time price from CoinGecko API
    token_id: 'ethereum', 'uniswap', etc.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = data[token_id][vs_currency]
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def get_multiple_prices(token_ids, vs_currency="usd"):
    """
    Fetch multiple token prices at once
    """
    ids = ",".join(token_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={vs_currency}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def get_token_market_data(token_id="ethereum"):
    """
    Fetch detailed market data (price, market cap, volume, etc.)
    """
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "name": data["name"],
            "symbol": data["symbol"].upper(),
            "price": data["market_data"]["current_price"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"],
            "volume_24h": data["market_data"]["total_volume"]["usd"],
            "price_change_24h": data["market_data"]["price_change_percentage_24h"],
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None
