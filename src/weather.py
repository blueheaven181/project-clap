import requests

def get_weather():

    try:

        url = "https://wttr.in/Abu Dhabi?format=j1"

        response = requests.get(url, timeout=10)

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

        weather_advice = ""

        if int(feels_like) > 35:
        
            weather_advice = (
            " Marc, temperatures are very high today. "
            "Please stay hydrated. You might get barbecued outside."
            )

        elif int(feels_like) < 20:
            weather_advice = (
            " Marc, it's quite chilly outside today. "
            "Consider bringing a jacket."
            )

        elif int(chance_of_rain) > 50:
            weather_advice = (
            " Marc, there is a high chance of rain today. "
            "Don't forget your umbrella."
            )

        return (
            f"Weather in Abu Dhabi is {temperature} degrees Celsius with {description}, "
            f"Feels like {feels_like} degrees Celsius. "
            f"Humidity is {humidity} percent, "
            f"Wind speed is {wind_speed} kilometers per hour, "
            f"Chance of rain is {chance_of_rain} percent, "
            f"Today's high will be {high_temp} degrees Celsius and the low will be {low_temp} degrees Celsius,"
            f"{weather_advice}"
        )

    except Exception as e:

        print("Weather error:", e)

        return (
        "Weather information is currently unavailable."
        )



if __name__ == "__main__":
    print(get_weather())