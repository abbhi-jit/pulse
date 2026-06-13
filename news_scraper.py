import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets loaded from GitHub Actions environment
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# We use RSS feeds for these websites as it is the most reliable way to "scrape" news structures that don't constantly break.
NEWS_SOURCES = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "NYT World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
}

def scrape_news():
    """Scrapes top 3 headlines from the 3 news websites."""
    all_news_html = ""
    
    for site_name, url in NEWS_SOURCES.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the XML (RSS) using BeautifulSoup
            soup = BeautifulSoup(response.content, features="xml")
            
            # Find all "item" tags (which contain the news articles)
            articles = soup.findAll('item')
            
            all_news_html += f"<h2>{site_name}</h2><ul>"
            
            # Get only the top 3 headlines
            for a in articles[:3]:
                title = a.title.text
                link = a.link.text
                pub_date = a.pubDate.text if a.pubDate else "No date"
                
                all_news_html += f"<li><strong>{pub_date}</strong>: <a href='{link}'>{title}</a></li>"
                
            all_news_html += "</ul>"
            
        except Exception as e:
            all_news_html += f"<h2>{site_name}</h2><p>Failed to scrape: {e}</p>"
            print(f"Failed to scrape {site_name}: {e}")

    return all_news_html

def send_news_email(html_content):
    """Sends the compiled HTML news report via Gmail."""
    if not EMAIL_SENDER:
        print("❌ Missing email secrets.")
        return

    msg = MIMEMultipart("alternative")
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = "📰 Your Morning News Briefing"

    # HTML Email Template
    html_template = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h1 style="color: #2c3e50;">Morning Headlines</h1>
        <hr>
        {html_content}
        <hr>
        <p style="font-size: 12px; color: #888;">Automated by your Pulse Bot</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html_template, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Morning news email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    print("Scraping news...")
    news_html = scrape_news()
    print("Sending email...")
    send_news_email(news_html)
