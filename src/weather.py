import requests

def get_weather():

    url = "https://wttr.in/Abu Dhabi?format=j1"

    response = requests.get(url)

    data = response.json()

    current = data["current_condition"][0]

    today = data["weather"][0]

    temperature = current["temp_C"]
    description = current["weatherDesc"][0]["value"]

    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_speed = current["windspeedKmph"]

    chance_of_rain = today["hourly"][0]["chanceofrain"]

    high_temp = today["maxtempC"]
    low_temp = today["mintempC"]

    return (
        f"Weather in Abu Dhabi is {temperature} degrees Celsius with {description}, "
        f"Feels like {feels_like} degrees Celsius, "
        f"Humidity is {humidity} percent, "
        f"Wind speed is {wind_speed} kilometers per hour, "
        f"Chance of rain is {chance_of_rain} percent, "
        f"Today's high will be {high_temp} degrees Celsius and the low will be {low_temp} degrees Celsius,"
    )

if __name__ == "__main__":
    print(get_weather())