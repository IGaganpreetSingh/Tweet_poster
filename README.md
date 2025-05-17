# 📡 Blockchain-Tweet Automation Bot

Automatically posts tweets from a **`topics.json`** queue to your **X (Twitter) account**.  
Ideal for keeping your feed filled with the latest blockchain talking-points while you focus on bigger tasks.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Rename `env.template` to `.env` and fill in your Twitter API and Groq API credentials
5. Run the bot:
   ```bash
   python tweet_bot.py
   ```

## Prerequisites

- Python 3.10+
- X developer account with API credentials (API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
- Groq API key for AI-generated tweets using Llama model

## Tweet Generation

The bot uses Groq's Llama model to generate short, well-structured tweets about blockchain topics. The AI is instructed to create professional content without emojis, focusing on clear and concise information with relevant hashtags.

## News Tweet Bot

In addition to the standard topic-based tweet bot, there's also a news-based tweet bot that automatically:

1. Checks the Cointelegraph blockchain RSS feed every 5 minutes
2. Scrapes the latest article content when a new one is published
3. Generates an insightful tweet about the article using Groq's Llama model
4. Posts the tweet to your X account with a link to the original article

To start the news tweet bot:

```bash
python news_tweet_bot.py
```

For a single check (useful for scheduled tasks):

```bash
python news_tweet_bot.py --single-check
```

## Automation Options

### UNIX cron

```bash
crontab -e
# Tweet every day at 10 AM IST
0 10 * * * /path/to/your/repo/.venv/bin/python /path/to/your/repo/tweet_bot.py >> tweet.log 2>&1

# Run the news tweet bot continuously
@reboot /path/to/your/repo/.venv/bin/python /path/to/your/repo/news_tweet_bot.py >> news_tweet.log 2>&1
```

### GitHub Actions

You can run both bots using GitHub Actions by setting up the necessary workflows.

#### 1. Topic-Based Tweet Bot (Daily)

The `.github/workflows/tweet.yml` file is already set up for the daily topic-based tweets:

```yaml
name: Daily tweet
on:
  schedule:
    - cron: "30 4 * * *" # 10:00 IST → 04:30 UTC
jobs:
  tweet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.10" }
      - run: pip install -r requirements.txt
      - run: python tweet_bot.py
        env:
          API_KEY: ${{ secrets.API_KEY }}
          API_KEY_SECRET: ${{ secrets.API_KEY_SECRET }}
          ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
          ACCESS_TOKEN_SECRET: ${{ secrets.ACCESS_TOKEN_SECRET }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

#### 2. News-Based Tweet Bot (Every 10 Minutes)

The `.github/workflows/news_tweet.yml` file is set up to check for news articles every 10 minutes:

```yaml
name: News tweet bot
on:
  schedule:
    - cron: "*/10 * * * *" # Run every 10 minutes
  workflow_dispatch: # Allow manual trigger

jobs:
  check_and_tweet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Download history file if exists
        uses: actions/download-artifact@v3
        with:
          name: tweet-history
          path: ./
        continue-on-error: true

      - name: Run news tweet bot (single check)
        run: python news_tweet_bot.py --single-check
        env:
          API_KEY: ${{ secrets.API_KEY }}
          API_KEY_SECRET: ${{ secrets.API_KEY_SECRET }}
          ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
          ACCESS_TOKEN_SECRET: ${{ secrets.ACCESS_TOKEN_SECRET }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

      - name: Upload updated history file
        uses: actions/upload-artifact@v3
        with:
          name: tweet-history
          path: tweet_history.json
          retention-days: 1
```

### Setting Up GitHub Actions

To use GitHub Actions for both bots:

1. Fork or push this repository to GitHub
2. Go to Settings > Secrets and add your API keys:
   - API_KEY
   - API_KEY_SECRET
   - ACCESS_TOKEN
   - ACCESS_TOKEN_SECRET
   - GROQ_API_KEY
3. GitHub will automatically run the workflows according to the schedule
