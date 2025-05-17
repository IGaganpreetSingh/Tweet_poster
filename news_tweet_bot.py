import json, os, tweepy, textwrap, time, requests, argparse
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import groq
import datetime

load_dotenv()

# --- 1. Auth ---
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# Initialize Groq client
groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

# RSS feed URL
RSS_URL = "https://cointelegraph.com/rss/tag/blockchain"

# File to store latest article info
HISTORY_FILE = "tweet_history.json"


def load_history():
    """Load the history of processed articles from file"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_article_link": "", "last_check": ""}


def save_history(history):
    """Save the history of processed articles to file"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def check_latest_article():
    """Check the RSS feed for the latest article"""
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return None

    # Get the latest entry
    latest_entry = feed.entries[0]

    # Get the link and title
    article = {
        "title": latest_entry.title,
        "link": latest_entry.link,
        "published": latest_entry.published,
    }

    return article


def scrape_article_content(url):
    """Scrape the article content from the URL"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the article content - adjust selectors based on the actual page structure
        paragraphs = soup.select("div.post-content p")

        # Extract text from paragraphs
        content = []
        for p in paragraphs:
            content.append(p.get_text().strip())

        # Join paragraphs with newlines
        full_content = "\n".join(content)

        # Extract a summary (first few paragraphs)
        summary = "\n".join(content[:5])

        return {
            "title": (
                soup.select_one("h1.post__title").get_text().strip()
                if soup.select_one("h1.post__title")
                else ""
            ),
            "full_content": full_content,
            "summary": summary,
        }
    except Exception as e:
        print(f"Error scraping article: {e}")
        return {"title": "", "full_content": "", "summary": ""}


def generate_tweet_from_article(article_data):
    """Generate a tweet from the article data using Groq"""
    try:
        prompt = f"""
Title: {article_data['title']}

Content Summary:
{article_data['summary']}

Article Link: {article_data['link']}
"""

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a blockchain expert creating tweets about the latest news. Your tweets should be short, insightful, and professional. DO NOT use quotation marks or emojis. Include the article link at the end of the tweet. Focus on the key points and why they matter.",
                },
                {
                    "role": "user",
                    "content": f"Create a short, engaging tweet (max 240 characters not including the link) about this blockchain news article. Focus on the most important aspect. Do not use quotation marks or emojis. Include relevant hashtags. Make it sound natural and insightful. The tweet should end with the article link.\n\n{prompt}",
                },
            ],
            max_tokens=150,
            temperature=0.7,
        )

        tweet_text = response.choices[0].message.content.strip()
        # Strip any quotation marks
        tweet_text = tweet_text.strip("\"'")
        return tweet_text
    except Exception as e:
        print(f"Error generating tweet: {e}")
        # Fallback tweet
        return f"Latest blockchain news: {article_data['title']} {article_data['link']} #Blockchain #Crypto"


def post_tweet(tweet_text):
    """Post the tweet to Twitter"""
    try:
        res = client.create_tweet(text=tweet_text)
        print("Tweeted:", tweet_text, "→", res.data["id"])
        return True
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")
        return False


def single_check():
    """Perform a single check and tweet if there's a new article"""
    # Load history
    history = load_history()

    # Check for the latest article
    latest_article = check_latest_article()

    # If no articles found, exit
    if not latest_article:
        print("No articles found in feed.")
        return

    # Check if this is a new article
    if latest_article["link"] != history["last_article_link"]:
        print(f"New article found: {latest_article['title']}")

        # Scrape article content
        article_data = scrape_article_content(latest_article["link"])
        article_data["link"] = latest_article["link"]

        # Generate tweet
        tweet_text = generate_tweet_from_article(article_data)

        # Post tweet
        success = post_tweet(tweet_text)

        if success:
            # Update history
            history["last_article_link"] = latest_article["link"]
            history["last_check"] = datetime.datetime.now().isoformat()
            save_history(history)
    else:
        print(f"No new articles. Last checked: {history['last_check']}")


def main_loop():
    """Main loop that checks for new articles and tweets them"""
    while True:
        try:
            single_check()
            # Wait for 5 minutes before checking again
            time.sleep(300)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(300)  # Still wait 5 minutes on error


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Blockchain News Tweet Bot")
    parser.add_argument(
        "--single-check",
        action="store_true",
        help="Check once for new articles and exit (useful for scheduled runs)",
    )
    args = parser.parse_args()

    print("Starting blockchain news tweet bot...")
    print(f"Checking RSS feed: {RSS_URL}")

    if args.single_check:
        print("Running in single check mode")
        single_check()
    else:
        print("Running in continuous mode. Press Ctrl+C to stop")
        main_loop()
