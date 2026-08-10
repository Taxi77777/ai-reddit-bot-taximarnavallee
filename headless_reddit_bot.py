#!/usr/bin/env python3
"""
🤖 100% Zero-Touch Headless Reddit Cloud Bot for Taxi Marne-la-Vallée
Automatically posts AI-generated replies using session authentication 24/7 on GitHub Actions.
"""

import os
import json
import urllib.request
import urllib.parse
import sys
import datetime

sys.stdout.reconfigure(encoding='utf-8')

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

SUBREDDITS = CONFIG.get('subreddits', ['disneylandparis', 'ParisTravelGuide'])
KEYWORDS = CONFIG.get('keywords', ['cdg', 'orly', 'taxi', 'disney', 'transfer', 'chessy'])
SITE_URL = CONFIG.get('site_url', 'https://taximarnavallee.com')

OUTPUT_DIR = os.path.dirname(__file__)
REPLIED_FILE = os.path.join(OUTPUT_DIR, 'replied_posts.json')

replied_ids = set()
if os.path.exists(REPLIED_FILE):
    try:
        with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
            replied_ids = set(json.load(f))
    except Exception:
        pass

def fetch_recent_posts(subreddit):
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

def generate_ai_reply(title, text):
    combined = (title + " " + text).lower()
    
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

def post_comment_headless(submission_id, reply_text, session_token):
    """
    Posts a comment autonomously using Reddit session token.
    """
    url = "https://www.reddit.com/api/comment"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Cookie': f'reddit_session={session_token}; token={session_token}',
        'Authorization': f'Bearer {session_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = urllib.parse.urlencode({
        'thing_id': f't3_{submission_id}',
        'text': reply_text,
        'api_type': 'json'
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"✅ Comment posted successfully on post {submission_id}!")
            return True
    except Exception as e:
        print(f"Notice auto-posting comment to {submission_id}: {e}")
        return False

def main():
    print("=== 🤖 100% Headless Zero-Touch Cloud Bot Started ===")
    session_token = os.environ.get('REDDIT_SESSION_TOKEN')
    
    auto_posted_count = 0

    for sub in SUBREDDITS:
        print(f"Scanning r/{sub} for headless auto-posting...")
        posts = fetch_recent_posts(sub)
        
        for p in posts:
            pdata = p.get('data', {})
            pid = pdata.get('id', '')
            title = pdata.get('title', '')
            text = pdata.get('selftext', '')
            
            if pid in replied_ids:
                continue
                
            combined = (title + " " + text).lower()
            matched_kws = [kw for kw in KEYWORDS if kw in combined]
            
            if matched_kws:
                print(f"🎯 Opportunity found in r/{sub}: {title}")
                ai_reply = generate_ai_reply(title, text)
                
                if session_token:
                    print(f"🚀 AUTO-POSTING via Headless Cloud Bot to post {pid}...")
                    success = post_comment_headless(pid, ai_reply, session_token)
                    if success:
                        replied_ids.add(pid)
                        auto_posted_count += 1
                else:
                    replied_ids.add(pid)

    with open(REPLIED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(replied_ids), f, ensure_ascii=False, indent=2)

    print(f"✨ Run completed. {auto_posted_count} replies processed.")

if __name__ == '__main__':
    main()
