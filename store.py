import json
import csv


def storeCSV(data):
    parsedData = json.loads(data)
    parsedData.to_csv("data.csv")