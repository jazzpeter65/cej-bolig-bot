import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# Hent e-mail og adgangskode fra GitHub Secrets
FROM_EMAIL = os.environ.get("FROM_EMAIL")
FROM_PASSWORD = os.environ.get("FROM_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

# CEJ-søgelink med dine kriterier (under 8000 kr, lejligheder i København/Sjælland)
URL = "https://udlejning.cej.dk/find-bolig/overblik?collection=residences&monthlyPrice=0-8000&p=sj%C3%A6lland%2Ck%C3%B8benhavn&types=apartment"

# Filnavn til at huske tidligere opslag
PREVIOUS_FILE = "previous.txt"

def get_previous():
    try:
        with open(PREVIOUS_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def save_current(content):
    with open(PREVIOUS_FILE, "w") as f:
        f.write(content)

def send_sms(message_body):
    msg = MIMEText(message_body)
    msg["Subject"] = "Ny CEJ-lejlighed!"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.send_message(msg)

def check_site():
    print("Tjekker CEJ-siden...")
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.find_all("div", class_="property-list__item")
    current = "\n".join([item.get_text(strip=True) for item in listings])
    previous = get_previous()

    if current != previous and previous != "":
        print("Ny bolig fundet – sender SMS!")
        send_sms("Ny bolig under 8000 kr i København/Sjælland – tjek CEJ nu!")
    else:
        print("Ingen ændringer.")

    save_current(current)

# Start tjekket
check_site()
