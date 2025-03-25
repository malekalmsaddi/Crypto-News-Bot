import asyncio
import logging
import database
from pycoingecko import CoinGeckoAPI

logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

async def fetch_market_once():
    try:
        logger.info("🌐 Fetching market prices and data...")

        # Fetch prices
        prices_data = cg.get_price(
            ids=['bitcoin', 'ethereum', 'solana', 'binancecoin', 'cardano'],
            vs_currencies='usd',
            include_24hr_change=True
        )

        # Store prices per coin
        coins = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "ADA": "cardano"
        }
        for symbol, coin_id in coins.items():
            price = prices_data[coin_id]['usd']
            change = prices_data[coin_id]['usd_24h_change']
            database.update_market_price(symbol, price, change)

        logger.info("✅ Market prices stored successfully.")

        # Fetch global market summary
        global_data = cg.get_global()
        total_market_cap = float(global_data['total_market_cap']['usd'])
        total_volume = float(global_data['total_volume']['usd'])
        btc_dominance = global_data['market_cap_percentage']['btc']
        eth_dominance = global_data['market_cap_percentage']['eth']

        # Store summary
        database.update_market_summary(total_market_cap, total_volume, btc_dominance, eth_dominance)
        logger.info("✅ Market summary stored successfully.")

    except Exception as e:
        logger.error(f"❌ Error fetching/storing market data: {e}")

async def fetch_and_store_market_data():
    # ✅ Force fetch on startup
    await fetch_market_once()
    while True:
        await fetch_market_once()
        await asyncio.sleep(60)  # Repeat every 1 minute

def start_market_fetcher():
    loop = asyncio.get_event_loop()
    loop.create_task(fetch_and_store_market_data())
    logger.info("✅ Market data fetcher started.")