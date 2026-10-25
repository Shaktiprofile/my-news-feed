"""
The Daily 4: Multi-Source Independent Intelligence Digest (with Persistent Memory)

Multi-Source Pools:
1. AI & Technology (Data Analyst Focus):
   - The Decoder (AI Research, Models, Safety)
   - Ars Technica (In-depth Technical Journalism)
   - The Register (Enterprise Tech & Infrastructure)
2. Global Financial & Macro Event:
   - The Guardian Economics (Independent Trust-Owned Global Economics)
   - BBC Global Business (Public Independent International Reporting)
3. Indian Macro/Micro Economics:
   - Indian Express Economy (Policy, Fiscal, Regulatory Analysis)
   - The Hindu BusinessLine (Macroeconomic Trends, RBI, Industry)
4. Independent Indian Policy & Investigative Journalism:
   - The India Forum (Academic Economic & Social Policy Essays)
   - Frontline (Deep Investigative Public-Interest Journalism)

Schedule: 6-Hour Refresh (Zero Duplicates, Persistent History)
"""

import os
import re
import ssl
import json
import time
import urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from feedgen.feed import FeedGenerator

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading history: {e}")
    return set()

def save_history(history_set):
    try:
        history_list = list(history_set)[-500:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
        print(f"Saved {len(history_list)} articles to persistent history.")
    except Exception as e:
        print(f"Error saving history: {e}")

def fetch_data(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        return None

def clean_and_absolutize_html(soup_elem, base_url):
    if not soup_elem:
        return ""
    
    for tag in soup_elem(['script', 'style', 'iframe', 'form', 'button', 'input', 'noscript', 'aside', 'nav']):
        tag.decompose()

    for h1 in soup_elem.find_all('h1'):
        h1.decompose()
        
    for img in soup_elem.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(' ')[0]
        if src:
            if src.startswith('/'):
                img['src'] = base_url.rstrip('/') + src
            elif not src.startswith('http'):
                img['src'] = base_url.rstrip('/') + '/' + src
            else:
                img['src'] = src
        img['style'] = 'max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0; display: block;'
        
    for a in soup_elem.find_all('a', href=True):
        href = a['href']
        if href.startswith('/'):
            a['href'] = base_url.rstrip('/') + href
            
    return str(soup_elem)

# ==============================================================================
# CATEGORY 1: AI & TECHNOLOGY (MULTI-SOURCE POOL)
# ==============================================================================
def get_ai_tech_article(history):
    print("[1/4] Scanning AI & Technology multi-source pool...")
    sources = [
        {"name": "The Decoder", "url": "https://the-decoder.com/feed/", "base": "https://the-decoder.com", "body_sel": ".entry-content, article"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "base": "https://arstechnica.com", "body_sel": ".article-content, article"}
    ]
    
    for src in sources:
        print(f" -> Checking {src['name']}...")
        raw_xml = fetch_data(src['url'])
        if not raw_xml:
            continue
            
        try:
            soup_xml = BeautifulSoup(raw_xml, 'xml')
            items = soup_xml.find_all(['item', 'entry'])
            for item in items[:8]:
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                
                link_elem = item.find('link')
                link = ""
                if link_elem:
                    link = link_elem.get('href') or link_elem.get_text(strip=True)
                clean_link = link.split('?')[0] if link else ""
                
                if not clean_link or clean_link in history or title.lower() in history:
                    continue
                    
                print(f"   [NEW] Selected from {src['name']}: {title[:50]}...")
                art_bytes = fetch_data(clean_link)
                body_html = ""
                if art_bytes:
                    art_soup = BeautifulSoup(art_bytes.decode('utf-8', errors='ignore'), 'html.parser')
                    body_elem = art_soup.select_one(src['body_sel'])
                    if body_elem:
                        body_html = clean_and_absolutize_html(body_elem, src['base'])
                        
                if not body_html or len(body_html) < 200:
                    desc_elem = item.find(['description', 'summary'])
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    body_html = f"<p>{desc}</p>"
                    
                full_content = f"""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                    <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                        <span style="color: #1d4ed8; font-weight: bold; font-size: 13px; text-transform: uppercase;">🤖 AI & Tech &bull; {src['name']}</span>
                    </div>
                    <div class="article-body">
                        {body_html}
                    </div>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Independent Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">{src['name']}</a></p>
                    </div>
                </div>
                """
                return {
                    'category': 'AI & Tech',
                    'title': title,
                    'link': clean_link,
                    'content': full_content,
                    'pub_date': datetime.now(timezone.utc)
                }
        except Exception as e:
            print(f"Error scanning {src['name']}: {e}")
            
    return None

# ==============================================================================
# CATEGORY 2: GLOBAL FINANCIAL & MACRO EVENT (MULTI-SOURCE POOL)
# ==============================================================================
def get_global_event_article(history):
    print("[2/4] Scanning Global Financial & Economic multi-source pool...")
    sources = [
        {"name": "The Guardian Economics", "url": "https://www.theguardian.com/business/economics/rss", "base": "https://www.theguardian.com", "body_sel": "article, #maincontent"},
        {"name": "BBC Global Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "base": "https://www.bbc.com", "body_sel": "article, main"}
    ]
    
    for src in sources:
        print(f" -> Checking {src['name']}...")
        raw_xml = fetch_data(src['url'])
        if not raw_xml:
            continue
            
        try:
            soup_xml = BeautifulSoup(raw_xml, 'xml')
            items = soup_xml.find_all(['item', 'entry'])
            for item in items[:8]:
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                
                link_elem = item.find('link')
                link = ""
                if link_elem:
                    link = link_elem.get('href') or link_elem.get_text(strip=True)
                clean_link = link.split('?')[0] if link else ""
                
                if not clean_link or clean_link in history or title.lower() in history:
                    continue
                    
                print(f"   [NEW] Selected from {src['name']}: {title[:50]}...")
                art_bytes = fetch_data(clean_link)
                body_html = ""
                if art_bytes:
                    art_soup = BeautifulSoup(art_bytes.decode('utf-8', errors='ignore'), 'html.parser')
                    body_elem = art_soup.select_one(src['body_sel'])
                    if body_elem:
                        body_html = clean_and_absolutize_html(body_elem, src['base'])
                        
                if not body_html or len(body_html) < 200:
                    desc_elem = item.find(['description', 'summary'])
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    body_html = f"<p>{desc}</p>"
                    
                full_content = f"""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                    <div style="background: #fdf2f8; border-left: 4px solid #db2777; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                        <span style="color: #9d174d; font-weight: bold; font-size: 13px; text-transform: uppercase;">🌍 Major Global Event &bull; {src['name']}</span>
                    </div>
                    <div class="article-body">
                        {body_html}
                    </div>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Independent Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">{src['name']}</a></p>
                    </div>
                </div>
                """
                return {
                    'category': 'Global Event',
                    'title': title,
                    'link': clean_link,
                    'content': full_content,
                    'pub_date': datetime.now(timezone.utc)
                }
        except Exception as e:
            print(f"Error scanning {src['name']}: {e}")
            
    return None

# ==============================================================================
# CATEGORY 3: INDIAN MACRO/MICRO ECONOMICS (MULTI-SOURCE POOL)
# ==============================================================================
def get_indian_macro_article(history):
    print("[3/4] Scanning Indian Macro/Micro Economics multi-source pool...")
    sources = [
        {"name": "Indian Express Economy", "url": "https://indianexpress.com/section/business/economy/feed/", "base": "https://indianexpress.com", "body_sel": "#pcl-full-content, .story-details"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/feeder/default.rss", "base": "https://www.thehindubusinessline.com", "body_sel": ".contentbody, article"}
    ]
    
    for src in sources:
        print(f" -> Checking {src['name']}...")
        raw_xml = fetch_data(src['url'])
        if not raw_xml:
            continue
            
        try:
            soup_xml = BeautifulSoup(raw_xml, 'xml')
            items = soup_xml.find_all('item')
            for item in items[:8]:
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                
                link_elem = item.find('link')
                link = ""
                if link_elem:
                    link = link_elem.get('href') or link_elem.get_text(strip=True)
                clean_link = link.split('?')[0] if link else ""
                
                if not clean_link or clean_link in history or title.lower() in history:
                    continue
                    
                print(f"   [NEW] Selected from {src['name']}: {title[:50]}...")
                art_bytes = fetch_data(clean_link)
                body_html = ""
                if art_bytes:
                    art_soup = BeautifulSoup(art_bytes.decode('utf-8', errors='ignore'), 'html.parser')
                    body_elem = art_soup.select_one(src['body_sel'])
                    if body_elem:
                        body_html = clean_and_absolutize_html(body_elem, src['base'])
                        
                if not body_html or len(body_html) < 200:
                    desc_elem = item.find('description')
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    body_html = f"<p>{desc}</p>"
                    
                full_content = f"""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                    <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                        <span style="color: #15803d; font-weight: bold; font-size: 13px; text-transform: uppercase;">🇮🇳 Indian Economy &bull; {src['name']}</span>
                    </div>
                    <div class="article-body">
                        {body_html}
                    </div>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">{src['name']}</a></p>
                    </div>
                </div>
                """
                return {
                    'category': 'Indian Economy',
                    'title': title,
                    'link': clean_link,
                    'content': full_content,
                    'pub_date': datetime.now(timezone.utc)
                }
        except Exception as e:
            print(f"Error scanning {src['name']}: {e}")
            
    return None

# ==============================================================================
# CATEGORY 4: INDEPENDENT INDIAN POLICY & JOURNALISM (MULTI-SOURCE POOL)
# ==============================================================================
def get_indian_policy_article(history):
    print("[4/4] Scanning Independent Indian Policy & Journalism pool...")
    
    # 1. First check if The India Forum has an unread essay
    print(" -> Checking The India Forum...")
    tif_raw = fetch_data("https://www.theindiaforum.in/")
    if tif_raw:
        soup = BeautifulSoup(tif_raw.decode('utf-8', errors='ignore'), 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if any(p in href for p in ['/article/', '/society/', '/economy/', '/book-reviews/']):
                if len(text) > 15 and not any(x in href for x in ['/authors/', '/topics/']):
                    full_url = "https://www.theindiaforum.in" + href if href.startswith('/') else href
                    if full_url not in history and text.lower() not in history:
                        print(f"   [NEW] Found unread essay on The India Forum: {text[:50]}...")
                        art_bytes = fetch_data(full_url)
                        if art_bytes:
                            art_soup = BeautifulSoup(art_bytes.decode('utf-8', errors='ignore'), 'html.parser')
                            author_links = art_soup.find_all('a', href=re.compile(r'/authors/'))
                            authors = list(dict.fromkeys([x.get_text(strip=True) for x in author_links if x.get_text(strip=True)]))
                            author_byline = ", ".join(authors) if authors else "The India Forum"
                            
                            lead_img = art_soup.select_one('.node__content img, article img')
                            cover_html = ""
                            if lead_img and lead_img.get('src'):
                                src = lead_img['src']
                                if src.startswith('/'): src = "https://www.theindiaforum.in" + src
                                cover_html = f"<div style='margin-bottom: 20px;'><img src='{src}' style='max-width: 100%; height: auto; border-radius: 8px;'/></div>"
                                
                            body_elem = art_soup.select_one('.node__content .field--name-body') or art_soup.select_one('.node__content')
                            body_html = clean_and_absolutize_html(body_elem, "https://www.theindiaforum.in") if body_elem else ""
                            
                            if body_html and len(body_html) > 300:
                                full_content = f"""
                                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                                    <div style="background: #fefce8; border-left: 4px solid #ca8a04; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                                        <span style="color: #854d0e; font-weight: bold; font-size: 13px; text-transform: uppercase;">🏛️ Independent Policy & Society &bull; The India Forum</span>
                                    </div>
                                    <p style="color: #6b7280; font-size: 14px; margin-bottom: 16px;"><strong>Author:</strong> {author_byline}</p>
                                    {cover_html}
                                    <div class="article-body">{body_html}</div>
                                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Independent Source: <a href="{full_url}" target="_blank" style="color: #2563eb;">The India Forum</a></p>
                                    </div>
                                </div>
                                """
                                return {
                                    'category': 'Indian Policy',
                                    'title': text,
                                    'link': full_url,
                                    'content': full_content,
                                    'pub_date': datetime.now(timezone.utc)
                                }

    # 2. If no new India Forum essay, seamlessly pull from Frontline (The Hindu's deep investigative magazine)
    print(" -> Moving to Frontline (Investigative Policy Journalism)...")
    frontline_raw = fetch_data("https://frontline.thehindu.com/feeder/default.rss")
    if frontline_raw:
        try:
            soup_xml = BeautifulSoup(frontline_raw, 'xml')
            for item in soup_xml.find_all('item')[:8]:
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                link_elem = item.find('link')
                link = ""
                if link_elem:
                    link = link_elem.get('href') or link_elem.get_text(strip=True)
                clean_link = link.split('?')[0] if link else ""
                
                if not clean_link or clean_link in history or title.lower() in history:
                    continue
                    
                print(f"   [NEW] Selected from Frontline: {title[:50]}...")
                art_bytes = fetch_data(clean_link)
                body_html = ""
                if art_bytes:
                    art_soup = BeautifulSoup(art_bytes.decode('utf-8', errors='ignore'), 'html.parser')
                    body_elem = art_soup.select_one('.contentbody, article, .story')
                    if body_elem:
                        body_html = clean_and_absolutize_html(body_elem, "https://frontline.thehindu.com")
                        
                if not body_html or len(body_html) < 200:
                    desc_elem = item.find('description')
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    body_html = f"<p>{desc}</p>"
                    
                full_content = f"""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                    <div style="background: #fefce8; border-left: 4px solid #ca8a04; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                        <span style="color: #854d0e; font-weight: bold; font-size: 13px; text-transform: uppercase;">🏛️ Independent Policy & Investigation &bull; Frontline</span>
                    </div>
                    <div class="article-body">{body_html}</div>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Independent Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">Frontline</a></p>
                    </div>
                </div>
                """
                return {
                    'category': 'Indian Policy',
                    'title': title,
                    'link': clean_link,
                    'content': full_content,
                    'pub_date': datetime.now(timezone.utc)
                }
        except Exception as e:
            print(f"Error scanning Frontline: {e}")
            
    return None

def generate_feed(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    history = load_history()
    print(f"Loaded {len(history)} previously read articles from history.")
    
    fg = FeedGenerator()
    fg.id("https://the-daily-4.local")
    fg.title("The Daily 4: Multi-Source Independent Intelligence")
    fg.author({'name': 'Curated Intelligence Pipeline'})
    fg.link(href="https://the-daily-4.local", rel="alternate")
    fg.description("Exactly 4 unique, fresh articles every day curated across trusted independent global and Indian newsrooms.")
    fg.language("en")
    
    articles = []
    
    a1 = get_ai_tech_article(history)
    if a1: articles.append(a1)
    
    a2 = get_global_event_article(history)
    if a2: articles.append(a2)
    
    a3 = get_indian_macro_article(history)
    if a3: articles.append(a3)
    
    a4 = get_indian_policy_article(history)
    if a4: articles.append(a4)
    
    print(f"\nTotal fresh articles curated across all independent sources: {len(articles)}/4")
    
    for item in articles:
        fe = fg.add_entry()
        fe.id(item['link'])
        fe.title(item['title'])
        fe.link(href=item['link'])
        fe.content(item['content'], type="CDATA")
        fe.published(item['pub_date'] if isinstance(item['pub_date'], datetime) else datetime.now(timezone.utc))
        
        history.add(item['link'])
        history.add(item['title'].lower())
        
    save_history(history)
    
    output_path = os.path.join(output_dir, "feed.xml")
    fg.rss_file(output_path, pretty=True)
    print(f"Successfully generated RSS feed at: {os.path.abspath(output_path)}")
    
    html_preview_path = os.path.join(output_dir, "index.html")
    with open(html_preview_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily 4: Multi-Source Independent Digest</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 20px; line-height: 1.75; color: #1f2937; background: #f8fafc; }}
        header {{ margin-bottom: 36px; padding-bottom: 24px; border-bottom: 2px solid #e2e8f0; }}
        h1 {{ color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.5px; }}
        .meta-subtitle {{ color: #64748b; font-size: 15px; margin: 0; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .digest-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 32px; margin-bottom: 36px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
        .badge-ai {{ background: #eff6ff; color: #1d4ed8; }}
        .badge-global {{ background: #fdf2f8; color: #9d174d; }}
        .badge-indian {{ background: #f0fdf4; color: #15803d; }}
        .badge-policy {{ background: #fefce8; color: #854d0e; }}
        a.title-link {{ font-size: 24px; font-weight: 700; color: #0f172a; text-decoration: none; display: block; margin-bottom: 20px; line-height: 1.35; }}
        a.title-link:hover {{ color: #2563eb; }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .article-body p {{ margin-bottom: 18px; font-size: 16px; color: #334155; }}
        .feed-btn {{ display: inline-block; background: #0f172a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-size: 13px; font-weight: 600; float: right; }}
    </style>
</head>
<body>
    <header>
        <a href="feed.xml" class="feed-btn">🔗 Copy RSS Link</a>
        <h1>☕ The Daily 4</h1>
        <p class="meta-subtitle">Multi-source independent intelligence digest: 4 complete articles, zero paywalls, scanning across trusted newsrooms globally and nationally.</p>
    </header>
""")
        for item in articles:
            cat = item.get('category', 'Daily')
            badge_cls = 'badge-ai' if 'AI' in cat else ('badge-global' if 'Global' in cat else ('badge-indian' if 'Indian Economy' in cat else 'badge-policy'))
            f.write(f"""
    <div class="digest-card">
        <span class="badge {badge_cls}">{cat}</span>
        <a href="{item['link']}" target="_blank" class="title-link">{item['title']}</a>
        <div>{item['content']}</div>
    </div>
""")
        f.write("""
</body>
</html>
""")
    print(f"Successfully generated HTML preview at: {os.path.abspath(html_preview_path)}")

if __name__ == '__main__':
    generate_feed()
