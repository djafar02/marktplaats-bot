import requests
from bs4 import BeautifulSoup
import time

# Ton token et ton chat ID
TOKEN = "8227420826:AAG5C8avrouBetCNYwuw-9dHiUdYaj4mjcU"
CHAT_ID = "1218899186"

# URL de la catégorie "Complete Keuken"
URL = "https://www.marktplaats.nl/l/huis-en-inrichting/keukens-complete-keukens/"

# Fonction pour envoyer un message Telegram
def send_message(text, photo=None):
    if photo:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        data = {"chat_id": CHAT_ID, "caption": text}
        files = {"photo": requests.get(photo).content}
        requests.post(url, data=data, files={"photo": ("image.jpg", files["photo"])})
    else:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}")

# Fonction pour récupérer les annonces
def get_ads():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    ads = []

    for item in soup.select("li.Search-listItem"):
        title = item.select_one("h3").get_text(strip=True) if item.select_one("h3") else "Sans titre"
        price = item.select_one("span.price").get_text(strip=True) if item.select_one("span.price") else "Prix inconnu"
        location = item.select_one("span.location-name").get_text(strip=True) if item.select_one("span.location-name") else "Localisation inconnue"
        link = "https://www.marktplaats.nl" + item.find("a")["href"] if item.find("a") else "Pas de lien"
        photo = item.find("img")["src"] if item.find("img") else None

        ads.append({
            "title": title,
            "price": price,
            "location": location,
            "link": link,
            "photo": photo
        })

    return ads

# ---------- Programme principal ----------
print("🤖 Bot démarré...")

# 1. Envoie les 3 dernières annonces dès le démarrage
ads = get_ads()[:3]
for ad in ads:
    text = f"📌 {ad['title']}\n💰 {ad['price']}\n📍 {ad['location']}\n🔗 {ad['link']}"
    send_message(text, ad["photo"])

# 2. Ensuite, surveille en continu
seen = set(ad["link"] for ad in ads)

while True:
    new_ads = get_ads()
    for ad in new_ads:
        if ad["link"] not in seen:
            text = f"🆕 {ad['title']}\n💰 {ad['price']}\n📍 {ad['location']}\n🔗 {ad['link']}"
            send_message(text, ad["photo"])
            seen.add(ad["link"])
    time.sleep(60)  # attends 1 minute entre chaque recherche
