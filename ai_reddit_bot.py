#!/usr/bin/env python3
"""
🤖 100% Autonomous AI Reddit Marketing Bot for Taxi Marne-la-Vallée
Runs 24/7 in the Cloud (GitHub Actions) even with your computer turned OFF!

Modes:
- AUTO-POST MODE: If REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD secrets exist,
  it automatically posts the AI-generated replies directly to Reddit 24/7 without human intervention.
- DASHBOARD MODE: Updates index.html & opportunities.json for GitHub Pages tracking.
"""

import os
import json
import urllib.request
import datetime
import sys

# UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

# Check if PRAW is available for auto-posting
try:
    import praw
    HAS_PRAW = True
except ImportError:
    HAS_PRAW = False

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

SUBREDDITS = CONFIG.get('subreddits', ['disneylandparis', 'ParisTravelGuide'])
KEYWORDS = CONFIG.get('keywords', ['cdg', 'orly', 'taxi', 'disney', 'transfer', 'chessy'])
SITE_URL = CONFIG.get('site_url', 'https://taximarnavallee.com')

OUTPUT_DIR = os.path.dirname(__file__)
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'index.html')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'opportunities.json')
REPLIED_FILE = os.path.join(OUTPUT_DIR, 'replied_posts.json')

# Load previously replied posts
replied_ids = set()
if os.path.exists(REPLIED_FILE):
    try:
        with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
            replied_ids = set(json.load(f))
    except Exception:
        pass

def get_reddit_client():
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    username = os.environ.get('REDDIT_USERNAME')
    password = os.environ.get('REDDIT_PASSWORD')

    if HAS_PRAW and client_id and client_secret and username and password:
        print("⚡ Reddit API credentials found! 100% Autonomous 24/7 Cloud Auto-Posting Enabled.")
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=f"TaxiMLV-Bot/1.0 by /u/{username}"
        )
    else:
        print("ℹ️ Reddit API credentials not set. Dashboard mode active.")
        return None

def fetch_reddit_posts_fallback(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('data', {}).get('children', [])
    except Exception as e:
        print(f"Warning fetching r/{subreddit}: {e}")
        return []

def generate_ai_response(post_title, post_text):
    title_lower = (post_title + " " + post_text).lower()
    
    route = "CDG / Orly Airport to Disneyland Paris"
    if "cdg" in title_lower:
        route = "Paris CDG Airport to Disneyland Paris"
    elif "orly" in title_lower:
        route = "Paris Orly Airport to Disneyland Paris"
    elif "night" in title_lower or "illuminations" in title_lower:
        route = "Late night transfer from Disney Park / Hotel"

    ai_reply = f"""Hi! Here is a breakdown of transport options for your trip ({route}):

1. **Direct Official Taxi / Private Transfer** (Recommended for families & groups):
   - Door-to-door directly to your hotel lobby.
   - Fixed rates (around €85-€95 from CDG/Orly).
   - Complimentary certified child seats & booster seats included.
   - No surge pricing late at night.

2. **Public Trains (RER B + RER A)**:
   - Cheaper for solo travelers (~€12/person), but requires changing trains at Châtelet with heavy luggage.

3. **Magic Shuttle Bus**:
   - ~€24/adult, ~€11/child. Stops at multiple hotels and takes 60-90 minutes.

*Full disclosure: I run a licensed local taxi service in Marne-la-Vallée ([taximarnavallee.com]({SITE_URL})). Feel free to ask any transport questions! Safe travels!*"""

    return ai_reply

def main():
    print("=== 🤖 100% Autonomous AI Reddit Cloud Bot Started ===")
    reddit_api = get_reddit_client()
    all_matches = []
    new_replies = 0

    if reddit_api:
        # 100% Autonomous Mode via PRAW API
        for sub_name in SUBREDDITS:
            print(f"Scanning r/{sub_name} via Official Reddit API...")
            try:
                subreddit = reddit_api.subreddit(sub_name)
                for submission in subreddit.new(limit=25):
                    if submission.id in replied_ids:
                        continue
                    
                    combined = (submission.title + " " + submission.selftext).lower()
                    matched_kws = [kw for kw in KEYWORDS if kw in combined]
                    
                    if matched_kws:
                        ai_reply = generate_ai_response(submission.title, submission.selftext)
                        
                        # POST AUTOMATICALLY 24/7 TO REDDIT
                        try:
                            print(f"🚀 AUTO-POSTING reply to: {submission.title}...")
                            submission.reply(ai_reply)
                            replied_ids.add(submission.id)
                            new_replies += 1
                            print("✅ Successfully posted reply automatically!")
                        except Exception as pe:
                            print(f"❌ Error auto-posting: {pe}")
                        
                        all_matches.append({
                            'subreddit': sub_name,
                            'title': submission.title,
                            'author': str(submission.author),
                            'date': datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'),
                            'url': f"https://www.reddit.com{submission.permalink}",
                            'keywords': matched_kws,
                            'text': submission.selftext[:200] + '...',
                            'ai_reply': ai_reply,
                            'posted_auto': True
                        })
            except Exception as se:
                print(f"Error scanning r/{sub_name} with API: {se}")
    else:
        # Fallback Scraper Mode for Dashboard
        for sub in SUBREDDITS:
            print(f"Scanning r/{sub} via Fallback Scraper...")
            posts = fetch_reddit_posts_fallback(sub)
            for p in posts:
                pdata = p.get('data', {})
                pid = pdata.get('id', '')
                title = pdata.get('title', '')
                text = pdata.get('selftext', '')
                combined = (title + " " + text).lower()
                
                matched_kws = [kw for kw in KEYWORDS if kw in combined]
                if matched_kws:
                    permalink = "https://www.reddit.com" + pdata.get('permalink', '')
                    author = pdata.get('author', 'user')
                    created_utc = pdata.get('created_utc', 0)
                    date_str = datetime.datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M')
                    
                    ai_reply = generate_ai_response(title, text)
                    
                    all_matches.append({
                        'subreddit': sub,
                        'title': title,
                        'author': author,
                        'date': date_str,
                        'url': permalink,
                        'keywords': matched_kws,
                        'text': text[:200] + '...',
                        'ai_reply': ai_reply,
                        'posted_auto': False
                    })

    # Save updated replied IDs
    with open(REPLIED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(replied_ids), f, ensure_ascii=False, indent=2)

    # Save JSON log
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

    # Build HTML Dashboard
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    status_text = f"⚡ 100% Autonomous Cloud Bot Active ({new_replies} auto-posted this run)" if reddit_api else "⚡ 24/7 Cloud Scanner Active"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>24/7 Autonomous AI Reddit Bot - Taxi Marne-la-Vallée</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Outfit', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
    .header {{ text-align: center; margin-bottom: 32px; }}
    h1 {{ font-size: 2.2rem; color: #f59e0b; margin-bottom: 8px; }}
    .status {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); display: inline-block; padding: 6px 16px; border-radius: 999px; font-weight: bold; font-size: 0.85rem; }}
    .card {{ background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1); border-left: 5px solid #f59e0b; }}
    .badge {{ background: #ff4500; color: #fff; padding: 4px 10px; border-radius: 999px; font-weight: bold; font-size: 0.8rem; }}
    .btn {{ display: inline-block; background: #10b981; color: #fff; text-decoration: none; padding: 10px 18px; border-radius: 10px; font-weight: bold; cursor: pointer; border: none; margin-top: 12px; }}
    .btn:hover {{ background: #059669; }}
    pre {{ background: #090d16; padding: 14px; border-radius: 10px; color: #cbd5e1; font-size: 0.85rem; white-space: pre-wrap; word-break: break-word; border: 1px solid #334155; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🤖 24/7 Autonomous AI Reddit Bot</h1>
    <div class="status">{status_text} · Last Run: {now_str}</div>
  </div>

  <div style="max-width: 900px; margin: 0 auto;">
"""

    if not all_matches:
        html += "<p style='text-align:center;'>No new Reddit transport questions detected in this run. Shortcuts below:</p>"
        html += """
        <div class="card" style="text-align:center;">
          <h3>🚀 Live Search Shortcuts</h3>
          <a href="https://www.reddit.com/r/disneylandparis/search/?q=CDG+OR+Orly+OR+taxi+OR+transfer&sort=new" target="_blank" class="btn">r/disneylandparis (CDG/Taxi)</a>
          <a href="https://www.reddit.com/r/ParisTravelGuide/search/?q=Disneyland+taxi+OR+transfer&sort=new" target="_blank" class="btn" style="background:#f59e0b; color:#0f172a; margin-left:10px;">r/ParisTravelGuide</a>
        </div>
        """
    else:
        for idx, m in enumerate(all_matches):
            auto_badge = " <span style='background:#10b981; color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;'>✅ AUTO-POSTED VIA API</span>" if m.get('posted_auto') else ""
            html += f"""
    <div class="card">
      <div><span class="badge">r/{m['subreddit']}</span>{auto_badge} <small style="color:#94a3b8;">u/{m['author']} • {m['date']}</small></div>
      <h3 style="margin: 10px 0 5px 0;">{m['title']}</h3>
      <p style="color:#cbd5e1; font-size:0.9rem;">{m['text']}</p>
      
      <h4 style="color:#f59e0b; margin-top:15px;">🤖 AI Generated Reply:</h4>
      <pre id="reply-{idx}">{m['ai_reply']}</pre>
      
      <a href="{m['url']}" target="_blank" class="btn">💬 View Thread on Reddit</a>
      <button onclick="copyReply('reply-{idx}')" class="btn" style="background:#f59e0b; color:#0f172a; margin-left:10px;">📋 Copy Reply</button>
    </div>
"""

    html += """
  </div>

  <script>
    function copyReply(id) {
      const text = document.getElementById(id).innerText;
      navigator.clipboard.writeText(text).then(() => {
        alert('AI Reply copied to clipboard!');
      });
    }
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✨ 24/7 Autonomous Bot run completed. Dashboard updated at {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
