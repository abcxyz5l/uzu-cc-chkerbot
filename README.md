# Telegram Card Checker Bot

A Telegram bot that processes text files containing card information and checks their validity.

## Features

- 📤 Upload text files with card data
- 💬 Reply to files with `/txt` command to start checking
- 🛑 Stop processing anytime with `/stop` command
- ✅ Get real-time results for each card
- 📊 Receive a summary after checking is complete

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/abcxyz5l/uzu-cc-chkerbot)

### Railway Deployment Steps:

1. **Fork this repository** to your GitHub account
2. **Go to [Railway.app](https://railway.app/)** and sign in with GitHub
3. **Click "New Project"** → "Deploy from GitHub repo"
4. **Select your forked repository**
5. **Add Environment Variable**:
   - Variable: `BOT_TOKEN`
   - Value: Your Telegram bot token (get from @BotFather)
6. **Deploy!** Railway will automatically install dependencies and start your bot

## Local Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 3. Configure the Bot

**Option A: Environment Variable (Recommended for Railway)**
```bash
# Windows
set BOT_TOKEN=your_bot_token_here

# Linux/Mac
export BOT_TOKEN=your_bot_token_here
```

**Option B: Edit the file directly (for local testing)**

The bot token is already set in the code, but you can change it in `telegram_bot.py`:

```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
```

### 4. Run the Bot

```bash
python telegram_bot.py
```

## How to Use

1. **Start the bot**: Send `/start` command to your bot
2. **Upload file**: Send a `.txt` file with card data
   - Format: `card_number|month|year|cvc`
   - Example: `4532123456789012|12|25|123`
3. **Start checking**: Reply to the file message with `/txt` command
4. **Stop anytime**: Send `/stop` command to stop the checking process

## File Format

Your text file should contain one card per line in this format:

```
4532123456789012|12|25|123
5425233430109903|01|26|456
4916338506082832|03|27|789
```

Format: `card_number|month|year|cvc`

## Results

The bot will send you real-time updates for each card:
- ✅ LIVE - Card is valid
- ❌ Card Declined - Card was declined
- 💰 Insufficient Funds - Card has no funds
- ⏰ Expired Card - Card has expired
- 🔢 Incorrect CVC - CVC is wrong
- And more...

## Commands

- `/start` - Start the bot and see instructions
- `/txt` - Process a text file (reply to file message)
- `/stop` - Stop the current checking process

## Deployment Files

- `Procfile` - Tells Railway how to run the bot
- `runtime.txt` - Specifies Python version
- `railway.json` - Railway configuration
- `requirements.txt` - Python dependencies

## Notes

⚠️ **Important**: This bot is for educational purposes only. Make sure you have permission to check the cards you're testing.

## Troubleshooting

- **Bot not responding**: Make sure the bot token is correct
- **File not processing**: Ensure the file format is correct (card|mm|yy|cvc)
- **Rate limiting**: The bot includes a 1-second delay between checks to avoid rate limiting
- **Railway deployment fails**: Check that BOT_TOKEN environment variable is set correctly

## Support

If you encounter any issues, make sure:
1. All dependencies are installed
2. Bot token is correctly configured (either in environment variable or code)
3. File format matches the expected format
4. You have a stable internet connection

## Repository

GitHub: [https://github.com/abcxyz5l/uzu-cc-chkerbot](https://github.com/abcxyz5l/uzu-cc-chkerbot)
