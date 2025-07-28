from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import webbrowser
from threading import Timer

app = Flask(__name__)
api_key = "c5de66ac52a07e1d0a52d342e266eabc"

EMOJILER = {
    "clear": "☀️",
    "partly cloudy": "⛅",
    "overcast cloudy": "☁️",
    "rainy": "🌧️",
    "laight rainy": "🌦️",
    "snow": "❄️",
    "fog": "🌫️",
    "storm": "⛈️",
    "broken clouds": "⛅" 
}

ARKA_PLANLAR = {
    "clear": "açık.jpg",
    "few clouds": "az_bulutlu.jpg",
    "scattered clouds": "parçalı_bulutlu.jpg",
    "broken clouds": "parçalı_az_bulutlu.jpg",
    "overcast clouds": "kapalı.jpg",
    "rain": "yağmurlu.jpg",
    "light rain": "hafif_yağmur.jpg",
    "snow": "kar.jpg",
    "mist": "sis.jpg",
    "thunderstorm": "fırtına.jpg"
}

@app.route("/", methods=["GET", "POST"])
def index():
    veri = None
    hata = None

    if request.method == "POST":
        sehir = request.form.get("sehir")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={api_key}&lang=eng&units=metric"
        cevap = requests.get(url)

        if cevap.status_code != 200:
            hata = "City not found. Please try again !"
        else:
            try:
                veri_json = cevap.json()
                dt_utc = veri_json["dt"]
                timezone_offset = veri_json["timezone"]
                lokal_zaman = datetime.utcfromtimestamp(dt_utc) + timedelta(seconds=timezone_offset)

                aciklama = veri_json["weather"][0]["description"].lower()

                arkaplan = "varsayilan.jpg"
                for anahtar in ARKA_PLANLAR:
                    if anahtar in aciklama:
                        arkaplan = ARKA_PLANLAR[anahtar]
                        break

                emoji = ""
                for anahtar in EMOJILER:
                    if anahtar in aciklama:
                        emoji = EMOJILER[anahtar]
                        break

                tahmin_listesi = []

                tahmin_url = f"https://api.openweathermap.org/data/2.5/forecast?q={sehir}&appid={api_key}&lang=eng&units=metric"
                tahmin_cevap = requests.get(tahmin_url)

                if tahmin_cevap.status_code == 200:
                    tahmin_json = tahmin_cevap.json()
                    gunler = {}

                    timezone_offset_forecast = tahmin_json["city"]["timezone"]

                    for item in tahmin_json["list"]:
                        zaman = datetime.utcfromtimestamp(item["dt"]) + timedelta(seconds=timezone_offset_forecast)
                        gun = zaman.strftime("%Y-%m-%d")
                        saat = zaman.hour
                        if gun not in gunler or abs(saat - 12) < abs(gunler[gun]["saat"] - 12):
                            gunler[gun] = {
                                "tarih": zaman.strftime("%d %B %A"),
                                "sicaklik": item["main"]["temp"],
                                "aciklama": item["weather"][0]["description"],
                                "icon": item["weather"][0]["icon"],
                                "saat": saat
                            }

                    tahmin_listesi = []
                    for i, g in enumerate(gunler.values()):
                        if i>=5:
                            break
                        g.pop("saat") 
                        tahmin_listesi.append(g)

                veri = {
                    "sehir": veri_json["name"],
                    "Sıcaklık": veri_json["main"]["temp"],
                    "Nem": veri_json["main"]["humidity"],
                    "Rüzgar": veri_json["wind"]["speed"],
                    "Açıklama": aciklama,
                    "Zaman": lokal_zaman.strftime('%Y-%m-%d %H:%M:%S'),
                    "emoji": emoji,
                    "arka_plan": arkaplan,
                    "tahminler": tahmin_listesi
                }

            except KeyError:
                hata = "Error occurred during data retrieval."

    return render_template("index.html", veri=veri, hata=hata)
@app.route ("/harita")
def harita():
    return render_template("harita.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
