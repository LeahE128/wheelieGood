import json
import csv
from sqlalchemy import create_engine
import pandas as pd
import config


def storeCSV(data):
    df.to_csv("data.csv")


engine = create_engine(f"mysql+mysqlconnector://{config.user}:{config.passw}@{config.uri}:3306/wheelieGood",
                           echo=True)
df = pd.read_sql("SELECT * from dynamic_bikes", engine)
storeCSV(df)