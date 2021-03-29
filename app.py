from flask import Flask, render_template
from jinja2 import Template
from sqlalchemy import create_engine
import config
from pandas import pandas as pd
from functools import lru_cache

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/about")
def about():
    return app.send_static_file("about.html")


@app.route("/currentBikes")
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
    res_df = df.set_index('last_update').resample('1d').mean()
    res_df['last_update'] = res_df.index
    return res_df.to_json(orient='records')


@app.route("/contact")
def contact():
    d = {'name': 'Team Wheelie Good'}
    return render_template("contact.html", **d)


if __name__ == "__main__":
    app.run(debug=True, port=5000)


