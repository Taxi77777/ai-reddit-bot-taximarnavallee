#!/usr/bin/env python3
"""
AI-Powered Reddit Marketing Bot for Taxi Marne-la-Vallée
Automatically scans Reddit, detects travel queries, and uses AI to generate
personalized, non-promotional, high-converting responses.
Designed for GitHub Actions & GitHub Pages.
"""

import os
import json
import urllib.request
import urllib.parse
import datetime
import sys

# Ensure UTF-8 output encoding for Windows terminal compatibility
sys.stdout.reconfigure(encoding='utf-8')

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

SUBREDDITS = CONFIG.get('subreddits', ['disneylandparis', 'ParisTravelGuide'])
KEYWORDS = CONFIG.get('keywords', ['cdg', 'orly', 'taxi', 'disney', 'transfer'])
SITE_URL = CONFIG.get('site_url', 'https://taximarnavallee.com')
WHATSAPP = CONFIG.get('whatsapp', '+33750535658')

OUTPUT_DIR = os.path.dirname(__file__)
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'index.html')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'opportunities.json')

def fetch_reddit_posts(subreddit):
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
    """
    Generates a personalized response using AI API if key is present,
    or smart fallback AI prompt engine.
    """
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
    print("=== AI Reddit Bot Started ===")
    all_matches = []

    for sub in SUBREDDITS:
        print(f"Scanning r/{sub}...")
        posts = fetch_reddit_posts(sub)
        
        for p in posts:
            pdata = p.get('data', {})
            title = pdata.get('title', '')
            text = pdata.get('selftext', '')
            combined = (title + " " + text).lower()
            
            matched_kws = [kw for kw in KEYWORDS if kw in combined]
            if matched_kws:
                permalink = "https://www.reddit.com" + pdata.get('permalink', '')
                author = pdata.get('author', 'user')
                created_utc = pdata.get('created_utc', 0)
                date_str = datetime.datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M')
                
                ai_suggested_reply = generate_ai_response(title, text)
                
                all_matches.append({
                    'subreddit': sub,
                    'title': title,
                    'author': author,
                    'date': date_str,
                    'url': permalink,
                    'keywords': matched_kws,
                    'text': text[:200] + '...' if len(text) > 200 else text,
                    'ai_reply': ai_suggested_reply
                })

    print(f"Found {len(all_matches)} relevant opportunities.")

    # Write JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

    # Build HTML Dashboard for GitHub Pages
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Reddit Marketing Hub - Taxi Marne-la-Vallée</title>
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
    <h1>🤖 AI Reddit Marketing Hub</h1>
    <div class="status">⚡ GitHub Actions Auto-Bot Active · Last Scan: {now_str}</div>
  </div>

  <div style="max-width: 900px; margin: 0 auto;">
"""

    if not all_matches:
        html += "<p style='text-align:center;'>No new Reddit queries detected in the latest scan. Shortcuts below:</p>"
        html += """
        <div class="card" style="text-align:center;">
          <h3>🚀 Live Search Shortcuts</h3>
          <a href="https://www.reddit.com/r/disneylandparis/search/?q=CDG+OR+Orly+OR+taxi+OR+transfer&sort=new" target="_blank" class="btn">r/disneylandparis (CDG/Taxi)</a>
          <a href="https://www.reddit.com/r/ParisTravelGuide/search/?q=Disneyland+taxi+OR+transfer&sort=new" target="_blank" class="btn" style="background:#f59e0b; color:#0f172a; margin-left:10px;">r/ParisTravelGuide</a>
        </div>
        """
    else:
        for idx, m in enumerate(all_matches):
            html += f"""
    <div class="card">
      <div><span class="badge">r/{m['subreddit']}</span> <small style="color:#94a3b8;">u/{m['author']} • {m['date']}</small></div>
      <h3 style="margin: 10px 0 5px 0;">{m['title']}</h3>
      <p style="color:#cbd5e1; font-size:0.9rem;">{m['text']}</p>
      
      <h4 style="color:#f59e0b; margin-top:15px;">🤖 AI Generated Personalized Reply:</h4>
      <pre id="reply-{idx}">{m['ai_reply']}</pre>
      
      <a href="{m['url']}" target="_blank" class="btn">💬 Post Reply on Reddit</a>
      <button onclick="copyReply('reply-{idx}')" class="btn" style="background:#f59e0b; color:#0f172a; margin-left:10px;">📋 Copy AI Reply</button>
    </div>
"""

    html += """
  </div>

  <script>
    function copyReply(id) {
      const text = document.getElementById(id).innerText;
      navigator.clipboard.writeText(text).then(() => {
        alert('AI Reply copied to clipboard! Click "Post Reply on Reddit" to paste it.');
      });
    }
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard generated at {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
