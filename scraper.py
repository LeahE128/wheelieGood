import requests
import sqlalchemy
from IPython.display import JSON
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import mysql.connector
import config
import time


stations_request = requests.get(config.STATIONS,
                                        params={"apiKey": config.APIKEY, "contract": config.NAME})

# Request Data from API
engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood", echo=True)

# Create static bike, dynamic bike & weather table & columns
meta = MetaData()

# Creating static bike table and columns
static_bikes = Table(
'static_bikes', meta,
Column('number', Integer),
Column('name', String(128)),
Column('address', String(128)),
Column('pos_lat', Float),
Column('pos_lng', Float),
Column('bike_stands', Integer)
)

# Creating dynamic bike table and columns
dynamic_bikes = Table(
'dynamic_bikes', meta,
Column('number', Integer),
Column('available_bike_stands', Integer),
Column('available_bikes', Integer),
Column('last_update', DateTime)
)

# Creating weather table and columns
weather = Table(
'weather', meta,
Column('weather_main', String(128)),
Column('weather_description', String(128)),
Column('weather_icon', String(128)),
Column('main_temp', Float),
Column('main_pressure', Integer),
Column('main_humidity', Integer),
Column('main_temp_min', Float),
Column('main_temp_max', Float),
Column('visibility', Integer),
Column('wind_speed', Float),
Column('wind_deg', Integer),
Column('clouds_all', Integer),
Column('dt', DateTime),
Column('sys_type', Integer),
Column('sys_id', Integer),
Column('sys_country', String(128)),
Column('sys_sunrise', DateTime),
Column('sys_sunset', DateTime),
Column('city_id', Integer),
Column('city_name', String(128)),
Column('cod', Integer)
)

meta.create_all(engine)


# Getting static bike data
def get_location(obj):
    return {'number': obj['number'],
            'name': obj['name'],
            'address': obj['address'],
            'pos_lng': obj['position']['lng'],
            'pos_lat': obj['position']['lat'],
            'bike_stands': obj['bike_stands']}


static = list(map(get_location, stations_request.json()))
print(static)
ins = static_bikes.insert().values(static)
engine.execute(ins)


# Getting dyanamic bike data
def get_station(obj):
    return {'number': obj['number'],
            'available_bike_stands': obj['available_bike_stands'],
            'available_bikes': obj['available_bikes'],
            'last_update': datetime.datetime.fromtimestamp(int(obj['last_update'] / 1e3))}


# Getting weather data
def get_weather(weather):
    weather = weather_request.json()

    weather['weather_id'] = weather['weather'][0]['id']
    weather['weather_main'] = weather['weather'][0]['main']
    weather['weather_description'] = weather['weather'][0]['description']
    weather['weather_icon'] = weather['weather'][0]['icon']
    weather['main_temp'] = weather['main']['temp']
    weather['main_pressure'] = weather['main']['pressure']
    weather['main_humidity'] = weather['main']['humidity']
    weather['main_temp_min'] = weather['main']['temp_min']
    weather['main_temp_max'] = weather['main']['temp_max']
    weather['visibility'] = weather['visibility']
    weather['wind_speed'] = weather['wind']['speed']
    weather['wind_deg'] = weather['wind']['deg']
    weather['clouds_all'] = weather['clouds']['all']
    weather['dt'] = datetime.datetime.fromtimestamp(int(weather['dt']))
    weather['sys_type'] = weather['sys']['type']
    weather['sys_id'] = weather['sys']['id']
    weather['sys_country'] = (weather['sys']['country'])
    weather['sys_sunrise'] = datetime.datetime.fromtimestamp(int(weather['sys']['sunrise']))
    weather['sys_sunset'] = datetime.datetime.fromtimestamp(int(weather['sys']['sunset']))
    weather['city_id'] = weather['id']
    weather['city_name'] = weather['name']
    weather['cod'] = weather['cod']

    return weather


# Execute every 5 minutes
while True:
    try:
        stations_request = requests.get(config.STATIONS,
                                        params={"apiKey": config.APIKEY, "contract": config.NAME})
        weather_request = requests.get(config.WEATHER_INFO,
                                       params={"appid": config.WAPIKEY, "id": config.WNAME})

        weather_insert = list(map(get_weather, weather_request.json()))
        engine.execute(weather.insert(), weather_insert)

        dynamic = list(map(get_station, stations_request.json()))
        ins = dynamic_bikes.insert().values(dynamic)
        engine.execute(ins)

        time.sleep(5 * 60)
    except:
        print("Please try again")
