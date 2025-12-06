import sys
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

# Specify the folder path where your HTML file is located
FOLDER_PATH = "saved"  # Change this to your folder name
HTML_FILE = os.path.join(FOLDER_PATH, "opinion.html")
XML_FILE = "articles.xml"
MAX_ITEMS = 500
BASE_URL = "https://www.banglanews24.com"

# Load HTML
if not os.path.exists(HTML_FILE):
    print("HTML not found")
    sys.exit(1)

with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

articles = []

def make_full_url(url):
    """Convert relative URL to absolute URL"""
    if url and not url.startswith("http"):
        return BASE_URL + url
    return url

# --- Find all articles with stretched-link ---
for container in soup.select("div.position-relative"):
    link = container.select_one("a.stretched-link")
    if not link:
        continue
    
    url = make_full_url(link.get("href", ""))
    if not url or "/opinion/news/bd/" not in url:
        continue
    
    # Get title (h1, h4, or h5)
    title_tag = container.select_one("h1, h4, h5")
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        continue
    
    # Get description
    desc_tag = container.select_one("p.text-limit-3, p")
    desc = desc_tag.get_text(strip=True) if desc_tag else ""
    
    # Get image
    img_tag = container.select_one("img")
    img = ""
    if img_tag:
        img = img_tag.get("src", "") or img_tag.get("srcset", "").split()[0]
        img = make_full_url(img) if img else ""
    
    # Get publication date (not present in this HTML, use current time)
    pub = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    articles.append({
        "url": url,
        "title": title,
        "desc": desc,
        "pub": pub,
        "img": img
    })

print(f"Found {len(articles)} articles")

# --- Load or create XML ---
if os.path.exists(XML_FILE):
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except ET.ParseError:
        root = ET.Element("rss", version="2.0")
else:
    root = ET.Element("rss", version="2.0")

# Ensure channel exists
channel = root.find("channel")
if channel is None:
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Banglanews24 Opinion"
    ET.SubElement(channel, "link").text = "https://www.banglanews24.com/category/opinion"
    ET.SubElement(channel, "description").text = "Latest opinion articles from Banglanews24"

# Deduplicate existing URLs
existing = set()
for item in channel.findall("item"):
    link_tag = item.find("link")
    if link_tag is not None:
        existing.add(link_tag.text.strip())

# Append new unique articles
new_count = 0
for art in articles:
    if art["url"] in existing:
        continue
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = art["title"]
    ET.SubElement(item, "link").text = art["url"]
    ET.SubElement(item, "description").text = art["desc"]
    ET.SubElement(item, "pubDate").text = art["pub"]
    if art["img"]:
        ET.SubElement(item, "enclosure", url=art["img"], type="image/jpeg")
    new_count += 1

print(f"Added {new_count} new articles")

# Trim to last MAX_ITEMS
all_items = channel.findall("item")
if len(all_items) > MAX_ITEMS:
    for old_item in all_items[:-MAX_ITEMS]:
        channel.remove(old_item)
    print(f"Trimmed to {MAX_ITEMS} items")

# Save XML
tree = ET.ElementTree(root)
ET.indent(tree, space="  ")  # Pretty print
tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

print(f"XML saved to {XML_FILE}")
print(f"Total items in XML: {len(channel.findall('item'))}")