import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

# Load Secrets
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def get_weather(city="Thiruvananthapuram"):
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Weather unavailable ({e})"

def get_quote():
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}" - {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"

def build_summary():
    today = date.today().strftime("%A, %d %B %Y")
    weather = get_weather()
    quote = get_quote()

    summary = f"""
======================================
  PULSE - Daily Summary
  {today}
======================================

WEATHER
  {weather}

TODAY'S QUOTE
  {quote}

======================================
"""
    return summary

def send_email(summary_text):
    if not EMAIL_SENDER:
        print("Missing Email Secrets!")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = " Your Daily Pulse Summary"

    # Attach the summary text to the email body
    msg.attach(MIMEText(summary_text, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER.split(","), msg.as_string())
        server.quit()
        print("Summary Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run():
    summary = build_summary()
    print(summary)
    
    # 1. Save it to a file (uploaded as a downloadable artifact)
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    # 2. Send it to your inbox!
    send_email(summary)

if __name__ == "__main__":
    run()
