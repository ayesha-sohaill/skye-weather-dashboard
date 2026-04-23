import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_KEY = "e6dafc1141765728508d5e1bb72634be"

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    url = base_url + "appid=" + API_KEY + "&q=" + city + "&units=metric"
    data = requests.get(url, timeout=5).json()

    if data.get("cod") != 200:
        return None

    return {
        "city":      data["name"],
        "country":   data["sys"]["country"],
        "temp":      round(data["main"]["temp"]),
        "feels":     round(data["main"]["feels_like"]),
        "humidity":  data["main"]["humidity"],
        "wind":      data["wind"]["speed"],
        "desc":      data["weather"][0]["description"].capitalize(),
        "icon":      data["weather"][0]["icon"],
    }

def get_forecast(city):
    url = "http://api.openweathermap.org/data/2.5/forecast?appid=" + API_KEY + "&q=" + city + "&units=metric&cnt=40"
    data = requests.get(url, timeout=5).json()

    if data.get("cod") != "200":
        return [], []

    # One reading per day at 12:00
    labels, temps = [], []
    seen = set()
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        time = item["dt_txt"].split(" ")[1]
        if date not in seen and time == "12:00:00":
            seen.add(date)
            labels.append(date[5:])   # show MM-DD only
            temps.append(round(item["main"]["temp"]))

    return labels, temps


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    labels  = []
    temps   = []
    error   = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather = get_weather(city)
            if weather:
                labels, temps = get_forecast(city)
            else:
                error = "City not found. Please check the spelling."

    return render_template("index.html",
                           weather=weather,
                           labels=labels,
                           temps=temps,
                           error=error)


if __name__ == "__main__":
    app.run(debug=True)