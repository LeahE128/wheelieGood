from flask import Flask, render_template
from jinja2 import Template
from sqlalchemy import create_engine
import config
import pandas as pd

app = Flask(__name__)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


@app.route("/about")
def about():
    return app.send_static_file("about.html")


@app.route("/bikes")
def dynamic_bikes():
    # Request Data from API
    engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
    df = pd.read_sql("SELECT * from dynamic_bikes", engine)
    weather_data = df.head(3).to_json(orient="records")
    return weather_data


@app.route("/contact")
def contact():
    d = {'name': 'Team Wheelie Good'}
    return render_template("contact.html", **d)


if __name__ == "__main__":
    app.run(debug=True, port=5000)