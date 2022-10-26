import datetime
import os
import requests
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy

API_KEY = os.environ["API_KEY"]
BASE_URL = "api.openweathermap.org/data/2.5/weather?"

app = Flask(__name__, 
            static_url_path="",
            static_folder="static",
            template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///weather.db"
app.config['SECRET_KEY'] = 'secret key'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return str(self.name)

#helper function to get weather data
def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={API_KEY}&units=metric'
    data = requests.get(url).json()
    return data

#helper function to get time
def get_date(timezone):
    tz = datetime.timezone(datetime.timedelta(seconds=int(timezone)))
    return datetime.datetime.now(tz=tz).time().hour

@app.route('/', methods=['POST'])
def index_post():
    #lower form input to avoid duplicates
    new_city = (request.form.get('city')).lower()
    err_msg = None

    #check if form contains anything
    if new_city:
        #check if city already exists in database
        if not City.query.filter_by(name=new_city).first():
            #check if city name entered correctly
            if get_weather(new_city)['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = "Incorrect city name. Please try again"
        else: 
            err_msg = "This city is already added"
    
    #send message
    if err_msg: 
        flash(err_msg,'error')
    else:
        flash("City added successfully!")
    
    return redirect(url_for('index_get'))

@app.route('/', methods=['GET'])
def index_get():
    cities = City.query.all()
    weather_data = []

    for city in cities: 
        data = get_weather(city)
        weather = {
            "city": city.name,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "time": get_date(data['timezone'])
        }

        weather_data.append(weather)
    return render_template("index.html",weather_data=weather_data)

@app.route('/delete/<city>', methods=['POST'])
def delete_city(city):
    city = City.query.filter_by(name=city).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Successfully deleted {city.name}', 'success')
    return redirect(url_for('index_get'))

if __name__ == '__main__':
    db.create_all()
    app.run()
