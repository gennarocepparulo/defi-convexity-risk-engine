import requests

def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    
    params = {
        "ids": "ethereum",
        "vs_currencies": "usd"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return data["ethereum"]["usd"]
