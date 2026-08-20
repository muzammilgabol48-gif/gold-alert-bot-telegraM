# XAUUSD Gold — AI News → Telegram Alert Bot

Ye bot har ghante gold (XAUUSD) ki latest news uthata hai, free AI (Groq/Llama)
se pucha jata hai bullish hai ya bearish, aur result seedha aapke Telegram pe
bhej deta hai — **bilkul automatic aur bilkul FREE**, bina aapke phone/laptop
on rakhe (GitHub ke free servers pe chalta hai).

---

## Setup — 5 Steps (ek dafa karna hai)

### 1. GitHub account + repo banayein
1. github.com pe free account banayein (agar nahi hai).
2. Naya **private** repository banayein, e.g. `gold-alert-bot`.
3. Is folder ki tamam files (`gold_alert.py`, `.github/workflows/gold-alert.yml`,
   ye `README.md`) us repo mein upload/push kar dein.

### 2. Groq API key (100% FREE, koi card nahi chahiye)
1. https://console.groq.com pe jayein, email ya Google se sign up karein.
2. "API Keys" section mein "Create API Key" dabayein.
3. Key copy kar ke save kar lein (gsk_ se shuru hogi).
   - Bilkul free hai — 14,400 requests/day tak, jo is bot ke liye
     (din mein 24 baar chalne pe) bohot zyada hai.

### 3. NewsAPI.org key (free)
1. https://newsapi.org/register pe free account banayein.
2. Dashboard se apni **API key** copy kar lein. (Free tier: 100 requests/day,
   jo is bot ke liye kaafi hai agar har ghante chalayein.)

### 4. Telegram Bot banayein (official, free, sabse reliable)
1. Apne phone mein Telegram app kholein, search bar mein **@BotFather**
   dhundein aur us se chat kholein.
2. `/newbot` command bhejein.
3. Bot ka ek naam poocha jayega (jaise "Gold Alert Bot") — koi bhi likh dein.
4. Phir ek **username** poocha jayega, ye unique aur `bot` pe khatam hona
   chahiye (jaise `mygoldalert_bot`).
5. BotFather aapko ek **token** dega jo kuch is tarah dikhega:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   — isko copy kar ke save kar lein, yehi `TELEGRAM_BOT_TOKEN` hai.
6. Ab apne naye bot ko Telegram mein dhundein (usi username se) aur usay
   koi bhi message bhejein (jaise "hi") — ye zaroori hai taake bot aapko
   pehchan sake.
7. Apne chat ID pata karne ke liye, browser mein ye URL kholein
   (apna token daal kar):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   Is page pe JSON dikhega, usme `"chat":{"id":123456789,...}` wala number
   dhundein — yehi aapka `TELEGRAM_CHAT_ID` hai.

### 5. GitHub Secrets add karein
Apne repo mein: **Settings → Secrets and variables → Actions → New repository secret**,
aur ye 4 secrets add karein:

| Secret Name           | Value                                      |
|------------------------|---------------------------------------------|
| `GROQ_API_KEY`         | Step 2 wali key                             |
| `NEWS_API_KEY`         | Step 3 wali key                             |
| `TELEGRAM_BOT_TOKEN`   | Step 4 wala bot token                       |
| `TELEGRAM_CHAT_ID`     | Step 4 wala chat id number                  |

---

## Bas ho gaya!

- GitHub Actions har ghante khud script run karega (aap **Actions** tab mein
  jaake "Run workflow" button se manually bhi test kar sakte hain).
- Agar naye headlines mein koi change nahi, alert nahi bhejega (duplicate
  spam se bachne ke liye).
- Har alert kuch is tarah dikhega:

  ```
  XAUUSD Gold Alert

  Bias: BULLISH
  Reason: Treasury buyback lowered yields, boosting demand for non-yielding gold.

  Top headline: [Reuters] Gold holds rally on lower Treasury yields...
  ```

## Customize karna ho to
- **Frequency**: `.github/workflows/gold-alert.yml` mein `cron: "5 * * * *"`
  line change karein (har ghante ki jagah har 30 min ke liye `*/30 * * * *`).
- **News query**: `gold_alert.py` mein `NEWS_QUERY` variable edit karein.
- **Model**: `GROQ_MODEL` variable mein koi bhi Groq-supported model daal
  sakte hain (e.g. `llama-3.1-8b-instant` for faster/lighter analysis).

## Poora system 100% Free hai
- **Groq AI** — free, no card required (14,400 req/day limit)
- **NewsAPI.org** — free tier (100 req/day)
- **Telegram Bot** — 100% free, official, unlimited
- **GitHub Actions** — free (2,000 min/month, ye bot bohot kam use karega)

## Limitations (honestly bata dena zaroori hai)
- Groq ka free tier open-source models (Llama) use karta hai — Claude/GPT
  jitna sharp analysis nahi hoga, lekin is simple bullish/bearish task ke
  liye kaafi accha hai.
- Ye trading signal/advice nahi hai — sirf news ka AI summary hai. Trading
  decisions apni risk management ke sath khud lein.
