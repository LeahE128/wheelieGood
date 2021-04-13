from flask import Flask, render_template
from jinja2 import Template
from sqlalchemy import create_engine
import config
from pandas import pandas as pd
from functools import lru_cache
import pickle
import requests
import df_reformatting

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
    df = pd.read_sql("SELECT * FROM wheelieGood.static_bikes ORDER BY name ASC;", engine)
    bike_data = df.to_json(orient="records")
    return bike_data


@app.route("/allBikes")
def all_bikes():
    # Request Data from API
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    # Joining both tables
    sql = """SELECT dynamic_bikes.number, available_bike_stands, available_bikes, last_update, name, address, pos_lat,
     pos_lng, bike_stands FROM wheelieGood.dynamic_bikes 
     INNER JOIN wheelieGood.static_bikes ON dynamic_bikes.number = static_bikes.number
     ORDER BY last_update ASC LIMIT 200;"""
    df = pd.read_sql(sql, engine)
    all_data = df.to_json(orient="records")
    return all_data

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
# Get Daily Bike information for Chart
def get_occupancy(station_id):
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    sql = f"""
    SELECT number, dayname(last_update) as day, 
    FLOOR(avg(available_bike_stands) + 0.5) AS avgStands, 
    FLOOR(avg(available_bikes) + 0.5) as avgBikes FROM  wheelieGood.dynamic_bikes
    WHERE number = {station_id}
    GROUP BY number, day
    Order by number, last_update ASC;
    """

    df = pd.read_sql_query(sql, engine)
    # res_df = df.set_index('last_update').resample('D').mean()
    # res_df['last_update'] = res_df.index
    return df.to_json(orient='records')


@app.route("/occupancyHourly/<int:station_id>")
@lru_cache
# Get Hourly Bike information for Chart
def get_occupancy_hourly(station_id):
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    sql = f"""
    SELECT number, last_update, available_bike_stands, available_bikes FROM  wheelieGood.dynamic_bikes
    WHERE number = {station_id}
    GROUP BY number, hour(last_update)
    order by number, last_update ASC;
    """

    df = pd.read_sql_query(sql, engine)
    res_df = df.set_index('last_update').resample('1h').mean()
    res_df['last_update'] = res_df.index
    return res_df.to_json(orient='records')

@app.route("/contact")
def contact():
    d = {'name': 'Team Wheelie Good'}
    return render_template("contact.html", **d)


@app.route("/RoutePlanner.html")
def route():
    d = {'name': 'Team Wheelie Good'}
    return render_template("/RoutePlanner.html", **d)


@app.route("/model/<int:station_id>/<int:hour>/<int:day>")
def model(station_id, hour, day):
    # get static bikes information too
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    static_bikes_df = pd.read_sql("SELECT * FROM wheelieGood.static_bikes ORDER BY name ASC;", engine)
    station_info = df_reformatting.reformatting_static_bikes(static_bikes_df, station_id)

    # parameters needed will be station number, hour (0-23) and day number (0-6)

    # call the forecast api and parse as a json
    forecast_request = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat=53.33306&lon=-6.24889&exclude=current,minutely&appid={config.forecast_api}")
    forecast_data = forecast_request.json()

    # parse the data for the desired row and return it as a list
    result = df_reformatting.formattingJson(forecast_data, hour, day)

    if result:
        # load the predictive model and get a prediction
        forestPrediction = pickle.load(open(f'pickle_jar/hourlyModels/randForest{station_id}.pkl', 'rb'))
        prediction = forestPrediction.predict(result)

    else:
        print("No data for this hour. Deferring to daily forecast.")
        result = df_reformatting.formattingDailyJson(forecast_data, day)
        forestPrediction = pickle.load(open(f'pickle_jar/dailyModels/randForest{station_id}.pkl', 'rb'))
        prediction = forestPrediction.predict(result)

    # numpy array cannot be sent to js, change to list to format to dictionary
    result = result[0]
    # add our predicted value to the weather info for js
    prediction = prediction.tolist()
    result.insert(0, prediction[0])

    filtered_result = result[4:10]

    # add a weather description to the list for the correct weather type
    weather_values = ["Clouds", "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm"]
    for index in range(len(filtered_result)):
        if filtered_result[index] == 1.0:
            result.insert(1, weather_values[index])

    result = result[0:5]
    result.extend((station_info[1], station_info[5]-prediction[0]))
    print(result)

    # zip the list to dictionary for return to js
    keys = ["predicted_bikes", "weather", "temp", "wind_speed", "humidity", "station_name", "predicted_available_stands"]
    prediction_output = dict(zip(keys, result))
    return prediction_output


if __name__ == "__main__":
    app.run(debug=True, port=5000)


