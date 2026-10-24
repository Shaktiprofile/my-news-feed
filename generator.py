"""
The Daily 4: High-Signal Independent Intelligence Digest
Curates exactly 4 complete articles a day (1 headline per category, full-text, 100% free):

1. AI & Technology (Data Analyst Focus) -> The Decoder (Full Article)
2. Global Financial & Economic Event    -> BBC Global Economy (Full Article)
3. Indian Macro/Micro Economic Headline -> Indian Express Economy (Full Article)
4. Independent Indian Policy & Society  -> The India Forum (Full Long-Form Essay)
"""

import os
import re
import ssl
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Setup SSL and Headers
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def fetch_html(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_and_absolutize_html(soup_elem, base_url):
    if not soup_elem:
        return ""
    
    # Remove junk
    for tag in soup_elem(['script', 'style', 'iframe', 'form', 'button', 'input', 'noscript', 'aside']):
        tag.decompose()

    # Remove top-level h1 tags if any to prevent duplicate title with card header
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
# CATEGORY 1: AI & TECHNOLOGY (DATA ANALYST FOCUS)
# ==============================================================================
def get_top_ai_article():
    print("[1/4] Fetching top AI & Technology headline...")
    xml_data = fetch_html("https://the-decoder.com/feed/")
    if not xml_data:
        return None
        
    try:
        root = ET.fromstring(xml_data)
        item = root.find('.//item')
        if item is None:
            return None
            
        title = item.find('title').text if item.find('title') is not None else "Untitled AI News"
        link = item.find('link').text if item.find('link') is not None else ""
        pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
        
        clean_link = link.split('?')[0]
        print(f" - Top AI Story: {title[:50]}...")
        
        art_html = fetch_html(clean_link)
        body_html = ""
        if art_html:
            soup = BeautifulSoup(art_html, 'html.parser')
            body_elem = soup.find('div', class_='entry-content') or soup.find('article')
            if body_elem:
                body_html = clean_and_absolutize_html(body_elem, "https://the-decoder.com")
                
        if not body_html:
            desc = item.find('description').text if item.find('description') is not None else ""
            body_html = f"<p>{desc}</p>"
            
        full_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <span style="color: #1d4ed8; font-weight: bold; font-size: 13px; text-transform: uppercase;">🤖 AI & Cutting-Edge Tech &bull; Daily Headline</span>
            </div>
            <div class="article-body">
                {body_html}
            </div>
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                <p style="margin: 0; font-size: 13px; color: #6b7280;">Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">The Decoder</a></p>
            </div>
        </div>
        """
        
        return {
            'category': 'AI & Tech',
            'badge': 'AI & Tech',
            'title': title,
            'link': clean_link,
            'content': full_content,
            'pub_date': pub_date_str or datetime.now(timezone.utc)
        }
    except Exception as e:
        print(f"Error fetching AI article: {e}")
        return None

# ==============================================================================
# CATEGORY 2: GLOBAL FINANCIAL & MACRO EVENT
# ==============================================================================
def get_top_global_article():
    print("[2/4] Fetching top Global Financial & Economic event...")
    xml_data = fetch_html("https://feeds.bbci.co.uk/news/business/rss.xml")
    if not xml_data:
        return None
        
    try:
        root = ET.fromstring(xml_data)
        item = root.find('.//item')
        if item is None:
            return None
            
        title = item.find('title').text if item.find('title') is not None else "Global Business Update"
        link = item.find('link').text if item.find('link') is not None else ""
        pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
        
        clean_link = link.split('?')[0]
        print(f" - Top Global Story: {title[:50]}...")
        
        art_html = fetch_html(clean_link)
        body_html = ""
        if art_html:
            soup = BeautifulSoup(art_html, 'html.parser')
            article_elem = soup.find('article') or soup.find('main')
            if article_elem:
                body_html = clean_and_absolutize_html(article_elem, "https://www.bbc.com")
                
        if not body_html:
            desc = item.find('description').text if item.find('description') is not None else ""
            body_html = f"<p>{desc}</p>"
            
        full_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
            <div style="background: #fdf2f8; border-left: 4px solid #db2777; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <span style="color: #9d174d; font-weight: bold; font-size: 13px; text-transform: uppercase;">🌍 Major Global Financial Event &bull; Daily Headline</span>
            </div>
            <div class="article-body">
                {body_html}
            </div>
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                <p style="margin: 0; font-size: 13px; color: #6b7280;">Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">BBC Global Business</a></p>
            </div>
        </div>
        """
        
        return {
            'category': 'Global Event',
            'badge': 'Global Event',
            'title': title,
            'link': clean_link,
            'content': full_content,
            'pub_date': pub_date_str or datetime.now(timezone.utc)
        }
    except Exception as e:
        print(f"Error fetching Global article: {e}")
        return None

# ==============================================================================
# CATEGORY 3: INDIAN MACRO/MICRO ECONOMIC HEADLINE
# ==============================================================================
def get_top_indian_macro_article():
    print("[3/4] Fetching top Indian Macro/Micro Economic headline...")
    xml_data = fetch_html("https://indianexpress.com/section/business/economy/feed/")
    if not xml_data:
        return None
        
    try:
        root = ET.fromstring(xml_data)
        item = root.find('.//item')
        if item is None:
            return None
            
        title = item.find('title').text if item.find('title') is not None else "Indian Economy News"
        link = item.find('link').text if item.find('link') is not None else ""
        pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
        
        clean_link = link.split('?')[0]
        print(f" - Top Indian Macro Story: {title[:50]}...")
        
        art_html = fetch_html(clean_link)
        body_html = ""
        if art_html:
            soup = BeautifulSoup(art_html, 'html.parser')
            content_elem = soup.find('div', id='pcl-full-content') or soup.find(class_='story-details')
            if content_elem:
                body_html = clean_and_absolutize_html(content_elem, "https://indianexpress.com")
                
        if not body_html:
            desc = item.find('description').text if item.find('description') is not None else ""
            body_html = f"<p>{desc}</p>"
            
        full_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
            <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <span style="color: #15803d; font-weight: bold; font-size: 13px; text-transform: uppercase;">🇮🇳 Indian Macro/Micro Economics &bull; Daily Headline</span>
            </div>
            <div class="article-body">
                {body_html}
            </div>
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                <p style="margin: 0; font-size: 13px; color: #6b7280;">Source: <a href="{clean_link}" target="_blank" style="color: #2563eb;">Indian Express Economy</a></p>
            </div>
        </div>
        """
        
        return {
            'category': 'Indian Economy',
            'badge': 'Indian Economy',
            'title': title,
            'link': clean_link,
            'content': full_content,
            'pub_date': pub_date_str or datetime.now(timezone.utc)
        }
    except Exception as e:
        print(f"Error fetching Indian Macro article: {e}")
        return None

# ==============================================================================
# CATEGORY 4: INDEPENDENT INDIAN POLICY & SOCIETY (THE INDIA FORUM)
# ==============================================================================
def get_top_india_forum_article():
    print("[4/4] Fetching top Independent Indian Policy essay (The India Forum)...")
    homepage_html = fetch_html("https://www.theindiaforum.in/")
    if not homepage_html:
        return None
        
    soup = BeautifulSoup(homepage_html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if any(prefix in href for prefix in ['/article/', '/society/', '/economy/', '/book-reviews/']):
            if len(text) > 15 and not any(x in href for x in ['/authors/', '/topics/']):
                full_url = "https://www.theindiaforum.in" + href if href.startswith('/') else href
                print(f" - Top India Forum Essay: {text[:50]}...")
                
                art_html = fetch_html(full_url)
                if not art_html:
                    continue
                    
                art_soup = BeautifulSoup(art_html, 'html.parser')
                author_links = art_soup.find_all('a', href=re.compile(r'/authors/'))
                authors = list(dict.fromkeys([a.get_text(strip=True) for a in author_links if a.get_text(strip=True)]))
                author_byline = ", ".join(authors) if authors else "The India Forum"
                
                cover_img_html = ""
                lead_img = art_soup.select_one('.node__content img, .field--name-field-image img, article img')
                if lead_img and lead_img.get('src'):
                    src = lead_img['src']
                    if src.startswith('/'):
                        src = "https://www.theindiaforum.in" + src
                    cover_img_html = f"<div style='margin-bottom: 20px;'><img src='{src}' style='max-width: 100%; height: auto; border-radius: 8px;'/></div>"
                    
                body_elem = art_soup.select_one('.node__content .field--name-body') or art_soup.select_one('.node__content')
                body_html = clean_and_absolutize_html(body_elem, "https://www.theindiaforum.in") if body_elem else f"<p><a href='{full_url}'>Read on The India Forum &rarr;</a></p>"
                
                full_content = f"""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; font-size: 16px;">
                    <div style="background: #fefce8; border-left: 4px solid #ca8a04; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                        <span style="color: #854d0e; font-weight: bold; font-size: 13px; text-transform: uppercase;">🏛️ Independent Indian Policy & Society &bull; Analytical Essay</span>
                    </div>
                    <p style="color: #6b7280; font-size: 14px; margin-bottom: 16px;"><strong>Author:</strong> {author_byline}</p>
                    {cover_img_html}
                    <div class="article-body">
                        {body_html}
                    </div>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                        <p style="margin: 0; font-size: 13px; color: #6b7280;">Source: <a href="{full_url}" target="_blank" style="color: #2563eb;">The India Forum</a></p>
                    </div>
                </div>
                """
                
                return {
                    'category': 'Indian Policy',
                    'badge': 'Indian Policy',
                    'title': text,
                    'link': full_url,
                    'content': full_content,
                    'pub_date': datetime.now(timezone.utc)
                }
                
    return None

def generate_feed(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    fg = FeedGenerator()
    fg.id("https://the-daily-4.local")
    fg.title("The Daily 4: Independent Intelligence Digest")
    fg.author({'name': 'Curated Intelligence Pipeline'})
    fg.link(href="https://the-daily-4.local", rel="alternate")
    fg.description("Exactly 4 complete articles a day: AI/Tech, Global Financial Event, Indian Macro/Micro Economics, and Indian Policy.")
    fg.language("en")
    
    articles = []
    
    # Collect exactly 1 top article per category
    a1 = get_top_ai_article()
    if a1: articles.append(a1)
    
    a2 = get_top_global_article()
    if a2: articles.append(a2)
    
    a3 = get_top_indian_macro_article()
    if a3: articles.append(a3)
    
    a4 = get_top_india_forum_article()
    if a4: articles.append(a4)
    
    print(f"\nTotal curated articles for today: {len(articles)}/4")
    
    for item in articles:
        fe = fg.add_entry()
        fe.id(item['link'])
        fe.title(item['title'])
        fe.link(href=item['link'])
        fe.content(item['content'], type="CDATA")
        fe.published(item['pub_date'] if isinstance(item['pub_date'], datetime) else datetime.now(timezone.utc))
        
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
    <title>The Daily 4: Curated Intelligence Digest</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 20px; line-height: 1.75; color: #1f2937; background: #f8fafc; }}
        header {{ margin-bottom: 36px; padding-bottom: 24px; border-bottom: 2px solid #e2e8f0; }}
        h1 {{ color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.5px; }}
        .meta-subtitle {{ color: #64748b; font-size: 15px; margin: 0; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 32px; margin-bottom: 36px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
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
        <p class="meta-subtitle">Your distraction-free daily intelligence digest: 4 complete articles, zero clickbait, 100% independent.</p>
    </header>
""")
        for item in articles:
            cat = item['category']
            badge_cls = 'badge-ai' if 'AI' in cat else ('badge-global' if 'Global' in cat else ('badge-indian' if 'Indian Economy' in cat else 'badge-policy'))
            f.write(f"""
    <div class="card">
        <span class="badge {badge_cls}">{item['category']}</span>
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
