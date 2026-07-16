import requests

def get_weather():

    url = (
        "https://wttr.in/Abu Dhabi?format=j1"
    )

    response = requests.get(url)

    data = response.json()

    temperature = data["current_condition"][0]["temp_C"]

    description = data["current_condition"][0]["weatherDesc"][0]["value"]

    return (
        f"Weather in Abu Dhabi is "
        f"{temperature} degrees Celsius "
        f"with {description}."

    )
