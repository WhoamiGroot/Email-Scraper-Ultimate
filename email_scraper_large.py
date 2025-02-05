# Python3
# Credit me: WhoamiGroot.
# Respect the rules and use it for legal Ethical Hacking only or Bug Hunting.
# I am not responsible for any misbehaviour of this tool.
# You know the rules and so do i..
# Happy hacking.

import requests
import urllib.parse
from bs4 import BeautifulSoup
from collections import deque
import re
from urllib.parse import urlparse
import time

# User-Agent Header to Mimic a Browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Get Target URL
user_url = input("[+] Enter Target URL To Scan: ").strip()
urls = deque([user_url])
scraped_urls = set()
emails = set()

# Extract target domain to restrict crawling
target_domain = urlparse(user_url).netloc

# Allow user to set max pages, try to prevent Rapid requests that can trigger anti-bot protections
try:
    MAX_PAGES = int(input("[+] Enter Maximum Number of Pages to Crawl: ").strip() or "100")
except ValueError:
    MAX_PAGES = 100

count = 0

try:
    while urls:
        count += 1
        if count > MAX_PAGES:
            break

        url = urls.popleft()
        scraped_urls.add(url)

        print(f"[{count}] Processing {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            response.raise_for_status()
        except (requests.RequestException, requests.exceptions.ConnectionError) as e:
            print(f"[-] Failed to fetch {url}: {e}")
            continue

        # Check if response is HTML
        if "text/html" not in response.headers.get("Content-Type", ""):
            print(f"[-] Skipping non-HTML content: {url}")
            continue

        # Extract Emails with improved regex
        new_emails = set(re.findall(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]{2,}", response.text))
        emails.update(new_emails)

        # Parse HTML for Links
        soup = BeautifulSoup(response.text, "lxml")

        # Iterate through links and process
        for anchor in soup.find_all("a", href=True):
            link = urllib.parse.urljoin(url, anchor["href"])

            # Follow all links, even external ones
            if link not in urls and link not in scraped_urls:
                urls.append(link)
                scraped_urls.add(link)

        # Introduce a delay to prevent rate-limiting
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[-] User Interruption! Exiting...")

# Print and Save Found Emails
if emails:
    print("\n[+] Emails Found:")
    with open("emails.txt", "w", encoding="utf-8") as f:
        for mail in emails:
            print(mail)
            f.write(mail + "\n")
    print("\n[+] Emails saved to emails.txt")
else:
    print("\n[-] No Emails Found.")

