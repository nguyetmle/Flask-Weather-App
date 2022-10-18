import os
import requests
from flask import Flask, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

API_KEY = os.environ["API_KEY"]
BASE_URL = "api.openweathermap.org/data/2.5/weather?"

app = Flask(__name__, 
            static_url_path="",
            static_folder="static",
            template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///weather.db"

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    cities = City.query.all()
    weather_data = []

    url = "api.openweathermap.org/data/2.5/weather?q={}&APPID=s347374cba0f7fbd2206babf350c6a3c7&units=metric"

    for city in cities: 
        # r = requests.get(f"{BASE_URL}q={}&APPID={API_KEY}&units=metric")
        data = requests.get(url.format(city.name)).json()
        print(data)
        weather = {
            "city": city.name,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }

        weather_data.append(weather)
    return render_template("index.html",weather_data=weather_data)
    # return render_template("index.html")

if __name__ == '__main__':
    app.run()
