from flask import Flask, render_template
from jinja2 import Template
from sqlalchemy import create_engine
import config
from pandas import pandas as pd
from functools import lru_cache
import pickle
import requests
import forecast_formatting

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/about")
def about():
    return app.send_static_file("about.html")


@app.route("/currentBikes")
@lru_cache
def current_bikes():
    # Request Data from API
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    # Using static bike table
    df = pd.read_sql('SELECT number, available_bike_stands, available_bikes, '
                     'MAX(last_update) FROM wheelieGood.dynamic_bikes dynB GROUP BY number;', engine)
    dynamic_bike_data = df.to_json(orient="records")
    return dynamic_bike_data


@app.route("/staticBikes")
def static_bikes():
    # Request Data from API
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    # Using static bike table
    df = pd.read_sql("SELECT * FROM wheelieGood.static_bikes;", engine)
    bike_data = df.to_json(orient="records")
    return bike_data

# @app.route("/allBikes")
# def all_bikes():
#     # Request Data from API
#     engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
#                            echo=True)
#     # Joining both tables
#     df = pd.read_sql("SELECT dynamic_bikes.number, available_bike_stands, available_bikes, last_update, name, address, pos_lat, pos_lng, bike_stands FROM wheelieGood.dynamic_bikes INNER JOIN wheelieGood.static_bikes ON dynamic_bikes.number = static_bikes.number;", engine)
#     all_data = df.to_json(orient="records")
#     return all_data

@app.route("/weather")
@lru_cache()
def dynamic_weather():
    # Request Data from API
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    # Using static bike table
    df = pd.read_sql("SELECT * from weather", engine)
    weather_data = df.to_json(orient="records")
    return weather_data


@app.route("/occupancy/<int:station_id>")
@lru_cache
def get_occupancy(station_id):
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    sql = f"""
    SELECT number, last_update, available_bike_stands, available_bikes FROM  wheelieGood.dynamic_bikes
    WHERE number = {station_id}
    GROUP BY number, day(last_update)
    order by number, last_update ASC;
    """

    df = pd.read_sql_query(sql, engine)
    res_df = df.set_index('last_update').resample('D').mean()
    res_df['last_update'] = res_df.index
    return res_df.to_json(orient='records')


@app.route("/contact")
def contact():
    d = {'name': 'Team Wheelie Good'}
    return render_template("contact.html", **d)


@app.route("/model/<int:station_id>/<int:hour>/<int:day>")
def model(station_id, hour, day):
    # parameters needed will be station number, hour (0-23) and day number (0-6)
    forecast_request = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat=53.33306&lon=-6.24889&exclude=current,minutely&appid={config.forecast_api}")
    forecast_data = forecast_request.json()

    # the desired row will be returned as a list
    result = forecast_formatting.formattingJson(forecast_data, station_id, hour, day)

    # load the predictive model and get a prediction
    forestPrediction = pickle.load(open('randomForestModel.pkl', 'rb'))
    prediction = forestPrediction.predict(result)

    # numpy array cannot be sent to js, change to list to format to dictionary
    prediction = prediction.tolist()

    # zip the result to a dictionary to send back to js
    keys = ["predicted_bikes"]
    prediction_output = dict(zip(keys, prediction))
    return prediction_output


if __name__ == "__main__":
    app.run(debug=True, port=5000)

