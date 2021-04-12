import pandas as pd
import numpy as np
import requests


def formattingJson(forecast_data, hour, day):
    # list weather rows to be added (from api doc)
    weatherConditions = ["Clouds", "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm"]

    # iterate over the json array to get the hourly data
    hourly_data = 0
    for k, v in forecast_data.items():
        if k == "hourly":
            hourly_data = v

    # create hourly data dataframe
    hourly_df = pd.DataFrame.from_dict(pd.json_normalize(hourly_data), orient='columns')
    hourly_df = hourly_df.reindex(hourly_df.columns.tolist() + weatherConditions, axis=1)

    weatherValues = []
    for x in hourly_df["weather"]:
        currentRow = x[0]
        for key, value in currentRow.items():
            if key == "main":
                weatherValues.append(value)

    # give new columns a value of 0 in all cells
    for col in hourly_df:
        hourly_df[col] = hourly_df[col].replace(np.nan).fillna(0)

    # where the
    for x in range(len(weatherValues)):
        for column in hourly_df.columns:
            if weatherValues[x] == column:
                hourly_df.at[x, column] = 1

    # get rid of the unneeded rows
    weather_df = hourly_df[["dt", "temp", "wind_speed", "humidity", "Clouds", "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm"]]

    # convert from unix epoch time to useable format...
    from datetime import datetime, timedelta
    start = datetime(1970, 1, 1)  # Unix epoch start time
    weather_df['datetime'] = weather_df.dt.apply(lambda x: start + timedelta(seconds=x))

    # Create new column weekday
    weather_df['weekday'] = weather_df['datetime'].dt.dayofweek
    # Create new column hour
    weather_df['hour'] = weather_df['datetime'].dt.hour

    # dump now defunct datetime column
    weather_df = weather_df.drop(columns=["dt", "datetime"])

    desired_row = weather_df[(weather_df["hour"] == hour) & (weather_df["weekday"] == day)].values.tolist()
    print(desired_row)

    return desired_row


def formattingDailyJson(forecast_data, day):
    # list weather rows to be added (from api doc)
    weatherConditions = ["Clouds", "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm"]

    # iterate over the json array to get the hourly data
    daily_data = 0
    for k, v in forecast_data.items():
        if k == "daily":
            daily_data = v

    # create dailly data dataframe
    daily_df = pd.DataFrame.from_dict(pd.json_normalize(daily_data), orient='columns')
    daily_df = daily_df.reindex(daily_df.columns.tolist() + weatherConditions, axis=1)

    weatherValues = []
    for x in daily_df["weather"]:
        currentRow = x[0]
        for key, value in currentRow.items():
            if key == "main":
                weatherValues.append(value)

    # give new columns a value of 0 in all cells
    for col in daily_df:
        daily_df[col] = daily_df[col].replace(np.nan).fillna(0)

    # where the values match the weather column, make 1
    for x in range(len(weatherValues)):
        for column in daily_df.columns:
            if weatherValues[x] == column:
                daily_df.at[x, column] = 1

    # get rid of the unneeded rows
    weather_df = daily_df[
        ["dt", "temp.day", "wind_speed", "humidity", "Clouds", "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm"]]

    # convert from unix epoch time to useable format...
    from datetime import datetime, timedelta
    start = datetime(1970, 1, 1)  # Unix epoch start time
    weather_df['datetime'] = weather_df.dt.apply(lambda x: start + timedelta(seconds=x))

    # Create new column weekday
    weather_df['weekday'] = weather_df['datetime'].dt.dayofweek

    # dump now defunct datetime column
    weather_df = weather_df.drop(columns=["dt", "datetime"])
    # the forecast returns a duplicate day, which will affect our model. we will drop the duplicate
    weather_df = weather_df.drop(weather_df.index[[7]])

    desired_row = weather_df[(weather_df["weekday"] == day)].values.tolist()
    print(desired_row)

    return desired_row
