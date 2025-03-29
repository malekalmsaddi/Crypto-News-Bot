import asyncio
import logging
from datetime import datetime
import database
from pycoingecko import CoinGeckoAPI
import shared 
import requests

logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()
_market_fetch_task = None

COINMARKETCAP_API_KEY = "479a8dc9-631e-4132-8c00-867c51f84431"
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

extra_coins = {
    "USDT": "tether",
    "XRP": "ripple",
    "USDC": "usd-coin",
    "DOGE": "dogecoin",
    "TRX": "tron",
    "STETH": "staked-ether",
    "WBTC": "wrapped-bitcoin",
    "LINK": "chainlink",
    "AVAX": "avalanche-2",
    "LEO": "leo-token",
    "XLM": "stellar",
    "WSTETH": "wrapped-steth",
    "SHIB": "shiba-inu",
    "HBAR": "hedera-hashgraph",
    "SUI": "sui",
    "DOT": "polkadot",
    "LTC": "litecoin"
}

async def fetch_market_once():
    print("🌐 Entered fetch_market_once()")
    try:
        logger.info("🌐 Fetching market prices and data from CoinGecko...")

        prices_data = await asyncio.to_thread(lambda: cg.get_price(
            ids=['bitcoin', 'ethereum', 'solana', 'binancecoin', 'cardano'],
            vs_currencies='usd',
            include_24hr_change=True
        ))

        coins = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "ADA": "cardano"
        }

        for symbol, coin_id in coins.items():
            if coin_id in prices_data:
                price = prices_data[coin_id]['usd']
                change = prices_data[coin_id].get('usd_24h_change', 0)
                database.update_market_price(symbol, price, change)

        logger.info("✅ Market prices stored successfully from CoinGecko.")

        global_data = await asyncio.to_thread(cg.get_global)
        if not global_data:
            raise Exception("Empty response from CoinGecko global data")

        total_market_cap = global_data.get('total_market_cap', {}).get('usd', 0)
        total_volume = global_data.get('total_volume', {}).get('usd', 0)
        market_cap_percentage = global_data.get('market_cap_percentage', {})

        database.update_market_summary(
            total_market_cap,
            total_volume,
            market_cap_percentage.get('btc', 0),
            market_cap_percentage.get('eth', 0)
        )

        logger.info("✅ Market summary stored successfully from CoinGecko.")

    except Exception as e:
        logger.error(f"❌ CoinGecko failed: {str(e)}. Trying CoinMarketCap fallback...", exc_info=True)
        fetch_market_from_coinmarketcap()

def fetch_market_from_coinmarketcap():
    try:
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }

        params = {
            'symbol': 'BTC,ETH,SOL,BNB,ADA',
            'convert': 'USD'
        }

        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        data = response.json()

        for symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'ADA']:
            if symbol in data['data']:
                quote = data['data'][symbol]['quote']['USD']
                price = quote['price']
                change = quote.get('percent_change_24h', 0)
                database.update_market_price(symbol, price, change)

        logger.info("✅ Fallback to CoinMarketCap successful.")

    except Exception as e:
        logger.error(f"❌ CoinMarketCap fallback failed: {str(e)}", exc_info=True)

def fetch_extra_coins_from_coinmarketcap():
    try:
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }

        params = {
            'symbol': ','.join(extra_coins.keys()),
            'convert': 'USD'
        }

        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        data = response.json()

        for symbol in extra_coins.keys():
            if symbol in data['data']:
                quote = data['data'][symbol]['quote']['USD']
                price = quote['price']
                change = quote.get('percent_change_24h', 0)
                database.update_market_price(symbol, price, change)

        logger.info("✅ Fallback to CoinMarketCap for extra coins successful.")

    except Exception as e:
        logger.error(f"❌ CoinMarketCap fallback for extra coins failed: {str(e)}", exc_info=True)

async def fetch_extra_coins_hourly():
    while not shared.is_shutting_down():
        try:
            logger.info("🕐 Fetching additional market data (hourly)...")
            try:
                prices_data = await asyncio.wait_for(asyncio.to_thread(lambda: cg.get_price(
                    ids=[coin_id for symbol, coin_id in extra_coins.items() if symbol != "USDT"],
                    vs_currencies='usd',
                    include_24hr_change=True
                )), timeout=10)
            except asyncio.TimeoutError:
                logger.warning("⚠️ CoinGecko extra coins fetch timed out — using CoinMarketCap fallback")
                fetch_extra_coins_from_coinmarketcap()
                await asyncio.sleep(3600)
                continue

            for symbol, coin_id in extra_coins.items():
                if symbol == "USDT":
                    continue

                if coin_id in prices_data:
                    coin_info = prices_data[coin_id]
                    price = coin_info.get('usd')
                    if price is not None:
                        change = coin_info.get('usd_24h_change', 0)
                        database.update_market_price(symbol, price, change)
                    else:
                        logger.warning(f"⚠️ Missing USD price for {symbol} ({coin_id}) in CoinGecko response.")
                else:
                    logger.warning(f"⚠️ {symbol} ({coin_id}) not found in CoinGecko response.")

            logger.info("✅ Hourly extra coins updated successfully from CoinGecko.")

        except Exception as e:
            logger.error(f"❌ Hourly CoinGecko fetch failed: {str(e)}. Trying CoinMarketCap fallback...", exc_info=True)
            fetch_extra_coins_from_coinmarketcap()

        await asyncio.sleep(3600)

async def fetch_and_store_market_data():
    print("📡 Entered fetch_and_store_market_data()")
    try:
        logger.info("🔄 Starting market data fetcher")
        try:
            await asyncio.wait_for(fetch_market_once(), timeout=10)
            logger.info("✅ Initial market fetch completed")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Initial market fetch timed out — continuing startup without data")

        while not shared.is_shutting_down():
            await asyncio.sleep(300)
            if shared.is_shutting_down():
                break
            await fetch_market_once()

    except asyncio.CancelledError:
        logger.info("🔕 Market fetcher task cancelled")
    finally:
        logger.info("⏹️ Market data fetching stopped")

def start_market_fetcher():
    print("🛰️ Inside start_market_fetcher()")
    global _market_fetch_task
    try:
        loop = asyncio.get_running_loop()
        task1 = loop.create_task(fetch_and_store_market_data())
        task2 = loop.create_task(fetch_extra_coins_hourly())
        _market_fetch_task = [task1, task2]
        logger.info("✅ Market data fetchers started successfully")
    except RuntimeError as e:
        logger.error(f"❌ Failed to start market fetcher: {str(e)}")

def stop_market_fetcher():
    global _market_fetch_task
    if _market_fetch_task:
        logger.info("⏹️ Stopping market fetchers...")
        for task in _market_fetch_task:
            if not task.done():
                task.cancel()
        _market_fetch_task = None