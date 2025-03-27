# CryptoNewsBot

CryptoNewsBot is a Telegram bot designed to provide cryptocurrency news, market updates, and price tracking. It uses the Telegram Bot API, CoinGecko API, and Flask for webhook handling.

## Features
- Fetch and display cryptocurrency market prices and summaries.
- Log and manage webhook events.
- Store and manage chat and message data using SQLite.
- Flask-based webhook server for Telegram bot integration.

## Requirements
- Python 3.8 or higher
- A Telegram Bot Token (from BotFather)
- CoinGecko API for market data

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd CryptoNewsBot
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install the required libraries using `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root and add the following:
```
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
WEBHOOK_URL=<your-webhook-url>
WEBHOOK_SECRET=<your-webhook-secret>
PORT=5000
HOST=0.0.0.0
DEBUG=True
DATABASE_FILE=bot_database.db
```

### 5. Initialize the Database
Run the following script to initialize the SQLite database:
```bash
python -c "from database import init_db; init_db()"
```

### 6. Run the Bot
Start the bot using Flask:
```bash
python app.py
```

## Project Structure
- `config.py`: Handles configuration and environment variables.
- `database.py`: Manages SQLite database interactions.
- `requirements.txt`: Lists all required Python libraries.
- `Required Libraries`: Documents the purpose and details of each dependency.

## Contributing
Feel free to fork the repository and submit pull requests for new features or bug fixes.

## License
This project is licensed under the MIT License.
