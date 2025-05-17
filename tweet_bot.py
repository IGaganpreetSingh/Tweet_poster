import json, os, tweepy, textwrap
from dotenv import load_dotenv
import groq

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

TOPIC_FILE = "topics.json"


# --- 2. Read topics ---
def load_topics(path=TOPIC_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_topics(topics, path=TOPIC_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)


# --- 3. Compose tweet with AI ---
def compose(topic: str) -> str:
    """Generate a tweet using Groq's Llama model."""
    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",  # Using Llama 3 model
            messages=[
                {
                    "role": "system",
                    "content": "You are a blockchain expert creating tweets. Your tweets should be short, insightful, and professional. DO NOT use any emojis or quotation marks. Focus on clear and concise information.",
                },
                {
                    "role": "user",
                    "content": f"Write a short, engaging tweet (under 240 characters) about: {topic}. Include relevant hashtags. Make it sound natural and insightful. Do not use any emojis or quotation marks. Keep it professional and well-structured.",
                },
            ],
            max_tokens=150,
            temperature=0.7,
        )

        tweet_text = response.choices[0].message.content.strip()
        # Strip any quotation marks from the beginning and end of the text
        tweet_text = tweet_text.strip("\"'")
        return textwrap.shorten(tweet_text, width=280, placeholder="…")
    except Exception as e:
        print(f"Error with Groq: {e}")
        # Fallback to a simple format if Groq fails
        return f"Latest on {topic}. #Blockchain #Crypto"


# --- 4. Publish & update file ---
def main():
    topics = load_topics()
    if not topics:
        print("No topics left – add more to topics.json.")
        return

    topic_obj = topics.pop(0)  # FIFO; use .pop(random) for random pick
    tweet_text = compose(topic_obj["topic"])

    try:
        res = client.create_tweet(text=tweet_text)
        print("Tweeted:", tweet_text, "→", res.data["id"])
        save_topics(topics)  # commits removal
    except tweepy.TweepyException as e:
        print("Error:", e)
        # roll back deletion if needed
        topics.insert(0, topic_obj)
        save_topics(topics)


if __name__ == "__main__":
    main()
