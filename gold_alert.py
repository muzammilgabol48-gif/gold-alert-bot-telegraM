"""
XAUUSD (Gold) News -> AI Analysis -> Telegram Alert
-----------------------------------------------------
1. Fetches latest gold/XAUUSD news headlines (NewsAPI.org)
2. Sends headlines to Groq (free AI API, Llama model) to judge Bullish / Bearish + reason
3. Sends the result to your Telegram via a Telegram Bot (official, free)
4. Avoids sending duplicate alerts using a small local state file

Required environment variables (set as GitHub Secrets - see README.md):
    GROQ_API_KEY         - your free Groq API key (console.groq.com, no card needed)
    NEWS_API_KEY         - your NewsAPI.org key (free tier)
    TELEGRAM_BOT_TOKEN   - token you got from @BotFather
    TELEGRAM_CHAT_ID     - your personal chat id (see README.md)
"""

import os
import json
import hashlib
import requests

# ---------- CONFIG ----------
NEWS_QUERY = "gold price OR XAUUSD OR bullion"
NEWS_PAGE_SIZE = 6
STATE_FILE = "last_alert_state.json"
GROQ_MODEL = "openai/gpt-oss-120b"

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_gold_news():
    """Fetch recent gold-related headlines from NewsAPI.org"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": NEWS_QUERY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": NEWS_PAGE_SIZE,
        "apiKey": NEWS_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    headlines = []
    for a in articles:
        title = a.get("title") or ""
        desc = a.get("description") or ""
        source = (a.get("source") or {}).get("name", "")
        if title:
            headlines.append(f"- [{source}] {title}. {desc}".strip())
    return headlines


def analyze_with_ai(headlines):
    """Ask Groq's free Llama model whether the news is bullish or bearish for XAUUSD"""
    news_text = "\n".join(headlines) if headlines else "No fresh headlines found."

    prompt = f"""You are a concise financial news analyst. Below are the latest gold/XAUUSD-related
news headlines. Decide whether the overall tone is BULLISH, BEARISH, or NEUTRAL for XAUUSD
(gold spot price), and give ONE short reason (max 2 sentences). This is for a personal WhatsApp
alert, so keep the whole reply under 60 words, plain text, no markdown, no disclaimers.

Headlines:
{news_text}

Reply in exactly this format:
Bias: <BULLISH/BEARISH/NEUTRAL>
Reason: <short reason>
"""

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def send_telegram(message):
    """Send a message via your Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.text


def load_last_hash():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f).get("hash")
        except Exception:
            return None
    return None


def save_last_hash(h):
    with open(STATE_FILE, "w") as f:
        json.dump({"hash": h}, f)


def main():
    headlines = fetch_gold_news()
    if not headlines:
        print("No headlines fetched, skipping.")
        return

    # Avoid re-sending the exact same set of headlines
    combined = "\n".join(headlines)
    current_hash = hashlib.sha256(combined.encode()).hexdigest()
    last_hash = load_last_hash()

    if current_hash == last_hash:
        print("No new headlines since last run, skipping alert.")
        return

    analysis = analyze_with_ai(headlines)
    message = f"XAUUSD Gold Alert\n\n{analysis}\n\nTop headline: {headlines[0][:180]}"

    result = send_telegram(message)
    print("Telegram send result:", result)

    save_last_hash(current_hash)


if __name__ == "__main__":
    main()
