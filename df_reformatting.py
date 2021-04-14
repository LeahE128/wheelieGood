import pandas as pd
import numpy as np
import requests


def format_mine(dataframe):
    icon_values = []
    weather_values = []
    for x in dataframe["weather"]:
        weather_items = x[0]
        for key, value in weather_items.items():
            if key == "main":
                weather_values.append(value)
            if key == "icon":
                icon_values.append(value)

    # give new columns a value of 0 in all cells
    for col in dataframe:
        dataframe[col] = dataframe[col].replace(np.nan).fillna(0)

    # insert icon values as column
    dataframe["icon"] = icon_values

    # where the weather values match, change from 0 to 1
    for x in range(len(weather_values)):
        for column in dataframe.columns:
            if weather_values[x] == column:
                dataframe.at[x, column] = 1

    # get rid of the unneeded rows
    weather_df = dataframe[["dt", "temp", "wind_speed", "humidity", "Clouds",
                            "Clear", "Snow", "Rain", "Drizzle", "Thunderstorm", "icon"]]

    # convert from unix epoch time to useable format...
    from datetime import datetime, timedelta
    # Unix epoch start time
    start = datetime(1970, 1, 1)
    weather_df['datetime'] = weather_df.dt.apply(lambda x: start + timedelta(seconds=x))

    # Create new column weekday
    weather_df['weekday'] = weather_df['datetime'].dt.dayofweek
    # Create new column hour
    weather_df['hour'] = weather_df['datetime'].dt.hour

    # dump now defunct datetime column
    weather_df = weather_df.drop(columns=["dt", "datetime"])

    return weather_df


def formatting_hourly_data(forecast_data, hour, day, weather_status):
    print("hello")
    # iterate over the json array to get the hourly data
    hourly_data = 0
    for key, value in forecast_data.items():
        if key == "hourly":
            hourly_data = value

    # create hourly data dataframe
    hourly_df = pd.DataFrame.from_dict(pd.json_normalize(hourly_data), orient='columns')
    hourly_df = hourly_df.reindex(hourly_df.columns.tolist() + weather_status, axis=1)
    print(hourly_df.head(1))

    weather_df = format_mine(hourly_df)

    # get the row as before, but we need to return a list for the ML
    values_to_return = weather_df[(weather_df["hour"] == hour) & (weather_df["weekday"] == day)].values.tolist()

    print("ReturningValues: ", values_to_return)

    return values_to_return


def formatting_daily_data(forecast_data, day, weather_status):
    # iterate over the json array to get the hourly data
    daily_data = 0
    for k, v in forecast_data.items():
        if k == "daily":
            daily_data = v

    # create dailly data dataframe
    daily_df = pd.DataFrame.from_dict(pd.json_normalize(daily_data), orient='columns')
    daily_df = daily_df.reindex(daily_df.columns.tolist() + weather_status, axis=1)
    daily_df = daily_df.rename(columns={'temp.day': 'temp'})

    weather_df = format_mine(daily_df)

    weatherValues = []
    for x in daily_df["weather"]:
        currentRow = x[0]
        for key, value in currentRow.items():
            if key == "main":
                weatherValues.append(value)

    # form the list to be returned
    values_to_return = weather_df[(weather_df["weekday"] == day)].values.tolist()
    values_to_return[0].pop(11)
    return values_to_return


def reformatting_static_bikes(static_data, number):
    desired_row = static_data[static_data["number"] == number]
    desired_list = list(desired_row.values)
    formatted_list = (desired_list[0])
    print(formatted_list)
    return formatted_list

