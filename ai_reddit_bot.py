#!/usr/bin/env python3
"""
🤖 100% Autonomous AI Reddit Marketing Bot for Taxi Marne-la-Vallée
Uses 403-proof Reddit RSS/Atom feeds to reliably scan travel posts 24/7 in GitHub Cloud.
"""

import os
import json
import urllib.request
import xml.etree.ElementTree as ET
import datetime
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Try loading PRAW if available
try:
    import praw
    HAS_PRAW = True
except ImportError:
    HAS_PRAW = False

# Load .env file if present
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as ef:
        for line in ef:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

SUBREDDITS = CONFIG.get('subreddits', ['disneylandparis', 'ParisTravelGuide', 'paris'])
KEYWORDS = CONFIG.get('keywords', ['cdg', 'orly', 'taxi', 'disney', 'transfer', 'chessy', 'shuttle', 'uber', 'hotel', 'seat', 'luggage', 'night'])
SITE_URL = CONFIG.get('site_url', 'https://taximarnavallee.com')

OUTPUT_DIR = os.path.dirname(__file__)
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'index.html')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'opportunities.json')
REPLIED_FILE = os.path.join(OUTPUT_DIR, 'replied_posts.json')

replied_ids = set()
if os.path.exists(REPLIED_FILE):
    try:
        with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
            replied_ids = set(json.load(f))
    except Exception:
        pass

def fetch_rss_posts(subreddit):
    """
    Fetches Reddit entries using the 100% reliable RSS/Atom feed.
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.rss"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    req = urllib.request.Request(url, headers=headers)
    entries = []
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                link_elem = entry.find('atom:link', ns)
                author_elem = entry.find('atom:author/atom:name', ns)
                updated_elem = entry.find('atom:updated', ns)
                content_elem = entry.find('atom:content', ns)
                id_elem = entry.find('atom:id', ns)
                
                title = title_elem.text if title_elem is not None else ''
                link = link_elem.attrib.get('href', '') if link_elem is not None else ''
                author = author_elem.text if author_elem is not None else 'anonymous'
                date_raw = updated_elem.text if updated_elem is not None else ''
                html_body = content_elem.text if content_elem is not None else ''
                post_id = id_elem.text if id_elem is not None else link
                
                # Clean HTML tags from body text
                clean_text = re.sub('<[^<]+?>', '', html_body)[:300]
                
                entries.append({
                    'id': post_id,
                    'title': title,
                    'link': link,
                    'author': author.replace('/u/', ''),
                    'date': date_raw[:16].replace('T', ' '),
                    'text': clean_text
                })
    except Exception as e:
        print(f"Error fetching r/{subreddit} RSS: {e}")
        
    return entries

def generate_ai_response(post_title, post_text):
    combined = (post_title + " " + post_text).lower()
    
    route = "CDG / Orly Airport to Disneyland Paris"
    if "cdg" in combined:
        route = "Paris CDG Airport to Disneyland Paris"
    elif "orly" in combined:
        route = "Paris Orly Airport to Disneyland Paris"
    elif "night" in combined or "illuminations" in combined:
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

import time

def main():
    print("=== 🤖 100% Autonomous AI Reddit Cloud Bot Started ===")
    all_matches = []

    for sub in SUBREDDITS:
        print(f"Scanning r/{sub} via 403-proof RSS...")
        entries = fetch_rss_posts(sub)
        print(f"Retrieved {len(entries)} entries from r/{sub}.")
        
        for e in entries:
            combined = (e['title'] + " " + e['text']).lower()
            matched_kws = [kw for kw in KEYWORDS if kw in combined]
            
            if matched_kws:
                ai_reply = generate_ai_response(e['title'], e['text'])
                
                all_matches.append({
                    'subreddit': sub,
                    'title': e['title'],
                    'author': e['author'],
                    'date': e['date'],
                    'url': e['link'],
                    'keywords': matched_kws,
                    'text': e['text'],
                    'ai_reply': ai_reply
                })
        
        time.sleep(2)

    print(f"Found {len(all_matches)} relevant opportunities across subreddits.")

    # Save JSON log
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

    # Build HTML Dashboard for GitHub Pages
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
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
    <div class="status">⚡ 403-Proof RSS Cloud Scanner Active · Last Scan: {now_str}</div>
  </div>

  <div style="max-width: 900px; margin: 0 auto;">
"""

    if not all_matches:
        html += "<p style='text-align:center;'>No new transport posts found in current scan cycle. Live shortcuts below:</p>"
        html += """
        <div class="card" style="text-align:center;">
          <h3>🚀 Live Search Shortcuts</h3>
          <a href="https://www.reddit.com/r/disneylandparis/search/?q=CDG+OR+Orly+OR+taxi+OR+transfer&sort=new" target="_blank" class="btn">r/disneylandparis (CDG/Taxi)</a>
          <a href="https://www.reddit.com/r/ParisTravelGuide/search/?q=Disneyland+taxi+OR+transfer&sort=new" target="_blank" class="btn" style="background:#f59e0b; color:#0f172a; margin-left:10px;">r/ParisTravelGuide</a>
        </div>
        """
    else:
        for idx, m in enumerate(all_matches):
            kw_badges = " ".join([f"<span style='background:#334155; padding:2px 6px; border-radius:4px; font-size:0.75rem;'>#{kw}</span>" for kw in m['keywords']])
            html += f"""
    <div class="card">
      <div><span class="badge">r/{m['subreddit']}</span> <small style="color:#94a3b8;">u/{m['author']} • {m['date']}</small></div>
      <h3 style="margin: 10px 0 5px 0;">{m['title']}</h3>
      <p style="color:#cbd5e1; font-size:0.9rem;">{m['text']}</p>
      <div style="margin-bottom:12px;">{kw_badges}</div>
      
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

    print(f"✨ Dashboard generated with {len(all_matches)} matches at {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
