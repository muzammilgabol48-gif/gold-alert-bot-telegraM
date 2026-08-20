"""
XAUUSD (Gold) News -> AI Analysis -> Telegram Alert
-----------------------------------------------------
1. Fetches latest USD economic calendar events (JBlanked API, sourced from Forex Factory)
2. Sends events to Groq (free AI API) to judge Bullish / Bearish + reason for XAUUSD
3. Sends the result to your Telegram via a Telegram Bot (official, free)
4. Avoids sending duplicate alerts using a small local state file

Required environment variables (set as GitHub Secrets - see README.md):
    GROQ_API_KEY         - your free Groq API key (console.groq.com, no card needed)
    JBLANKED_API_KEY      - your free JBlanked API key (jblanked.com/profile)
    TELEGRAM_BOT_TOKEN   - token you got from @BotFather
    TELEGRAM_CHAT_ID     - your personal chat id (see README.md)
"""

import os
import json
import hashlib
import requests

# ---------- CONFIG ----------
STATE_FILE = "last_alert_state.json"
GROQ_MODEL = "openai/gpt-oss-120b"
RELEVANT_CURRENCIES = {"USD"}  # gold (XAUUSD) mainly reacts to USD data
HIGH_IMPACT_ONLY = True
HIGH_IMPACT_LABELS = {"HIGH", "STRONG", "3"}  # covers different label styles the API may use

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
JBLANKED_API_KEY = os.environ["JBLANKED_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_gold_news():
    """Fetch today's USD economic calendar events from Forex Factory via JBlanked API"""
    url = "https://www.jblanked.com/news/api/forex-factory/calendar/today/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {JBLANKED_API_KEY}",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    events = resp.json()
    if isinstance(events, dict):
        events = events.get("results") or events.get("data") or []

    headlines = []
    for e in events:
        currency = (e.get("currency") or e.get("Currency") or "").upper()
        if RELEVANT_CURRENCIES and currency not in RELEVANT_CURRENCIES:
            continue

        strength = e.get("strength") or e.get("Strength") or ""
        if HIGH_IMPACT_ONLY:
            strength_label = str(strength).strip().upper()
            if strength_label not in HIGH_IMPACT_LABELS:
                continue

        name = e.get("name") or e.get("Name") or e.get("event") or "Event"
        actual = e.get("actual") or e.get("Actual") or "N/A"
        forecast = e.get("forecast") or e.get("Forecast") or "N/A"
        previous = e.get("previous") or e.get("Previous") or "N/A"
        headlines.append(
            f"- [{currency}] {name}: actual={actual}, forecast={forecast}, "
            f"previous={previous} {('impact=' + str(strength)) if strength else ''}".strip()
        )
    return headlines


def analyze_with_ai(events):
    """Ask Groq's free AI model whether the economic data is bullish or bearish for XAUUSD"""
    news_text = "\n".join(events) if events else "No fresh USD economic events found."

    prompt = f"""You are a concise financial news analyst. Below are today's latest USD economic
calendar events (from Forex Factory) that move gold (XAUUSD) prices. Decide whether the overall
tone is BULLISH, BEARISH, or NEUTRAL for XAUUSD (gold spot price), and give ONE short reason
(max 2 sentences). Remember: strong USD data (beats forecast) is usually BEARISH for gold, and
weak USD data (misses forecast) is usually BULLISH for gold. This is for a personal Telegram
alert, so keep the whole reply under 60 words, plain text, no markdown, no disclaimers.

Events:
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
            "max_completion_tokens": 600,
            "reasoning_effort": "low",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"].get("content") or ""
    content = content.strip()
    if not content:
        content = "Bias: UNKNOWN\nReason: AI response was empty this run, try again next cycle."
    return content


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
    events = fetch_gold_news()
    if not events:
        print("No relevant USD events found right now, skipping.")
        return

    combined = "\n".join(events)
    current_hash = hashlib.sha256(combined.encode()).hexdigest()
    last_hash = load_last_hash()

    if current_hash == last_hash:
        print("No new events since last run, skipping alert.")
        return

    analysis = analyze_with_ai(events)
    message = f"XAUUSD Gold Alert\n\n{analysis}\n\nLatest event: {events[0][:180]}"

    result = send_telegram(message)
    print("Telegram send result:", result)

    save_last_hash(current_hash)


if __name__ == "__main__":
    main()
