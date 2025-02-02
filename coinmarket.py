from coinmarketcapapi import CoinMarketCapAPI

# Create an instance of CoinMarketCapAPI with the provided API key
api_key = "f638cf06-1b14-4382-ba7c-d118a5ce6a88"
cmc = CoinMarketCapAPI(api_key=api_key)

def format_usd(value):
    """
    Returns the value formatted as USD currency if it's a number.
    If value is not numeric, returns it unchanged.
    """
    if isinstance(value, (int, float)):
        return f"${value:,.2f}"
    return value

# Retrieve the latest quote data for BTC
rep = cmc.cryptocurrency_quotes_latest(symbol='BTC')
data = rep.data.get("BTC", {})

# In case the retrieved data is a list, use the first element
if isinstance(data, list):
    data = data[0]

# Since the CoinMarketCap API returns the quotes in a nested dict,
# extract the USD quote directly instead of iterating through a list.
quote = data.get("quote", {}).get("USD", {})

# Extract the required fields safely using .get()
name = data.get("name", "N/A")
price = quote.get("price", "N/A")
percent_change_1h = quote.get("percent_change_1h", "N/A")
percent_change_24h = quote.get("percent_change_24h", "N/A")
percent_change_7d = quote.get("percent_change_7d", "N/A")
market_cap = quote.get("market_cap", "N/A")
volume_24h = quote.get("volume_24h", "N/A")
circulating_supply = data.get("circulating_supply", "N/A")
last_updated = data.get("last_updated", "N/A")

# Format numeric values as USD currency
price_formatted = format_usd(price)
market_cap_formatted = format_usd(market_cap)
volume_24h_formatted = format_usd(volume_24h)
circulating_supply_formatted = format_usd(circulating_supply)

# Print out the fields
print("Name:", name)
print("Price:", price_formatted)
print("1h %:", percent_change_1h)
print("24h %:", percent_change_24h)
print("7d %:", percent_change_7d)
print("Market Cap:", market_cap_formatted)
print("Volume(24h):", volume_24h_formatted)
print("Circulating Supply:", circulating_supply_formatted)
print("Last Updated:", last_updated)
