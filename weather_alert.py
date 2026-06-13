import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets loaded from GitHub Actions environment
OWM_API_KEY = os.environ.get("OWM_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
CITY = "London" # Change this to your city!

def send_email_alert(temp, description):
    """Sends an email alert using Gmail."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"⚠️ Weather Alert for {CITY}"

    body = f"Alert! The current temperature in {CITY} is {temp}°C with {description}.\n\nPlease prepare accordingly!"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
        server.quit()
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def check_weather():
    """Fetches weather from OpenWeatherMap and checks conditions."""
    if not OWM_API_KEY:
        print("❌ Missing OWM_API_KEY secret.")
        return

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OWM_API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"].lower()
        description = data["weather"][0]["description"]
        
        print(f"Current weather in {CITY}: {temp}°C, {description}")

        # Check XP Challenge Conditions: Temp > 35°C OR Rain is predicted
        if temp > 35 or "rain" in condition:
            print("🚨 Alert conditions met! Sending email...")
            send_email_alert(temp, description)
        else:
            print("🌤️ Weather is fine. No alert needed.")
            
    except Exception as e:
        print(f"❌ Could not fetch weather data: {e}")

if __name__ == "__main__":
    check_weather()
