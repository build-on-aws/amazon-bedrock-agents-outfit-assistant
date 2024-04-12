import requests
import os
import json

class WeatherFinder:
    @staticmethod
    def get_current_weather(lat, lon):
        # Retrieve the API key from an environment variable
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        units = "metric"

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}"
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad requests

            data = response.json()
            temp_max = data['main']['temp_max']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']

            return {
                "currentTemperature": temperature,
                "maxTemperature": temp_max,
                "humidity": humidity,
                "description": description
            }

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return {"error": "HTTP error occurred while retrieving weather data."}

        except requests.exceptions.RequestException as req_err:
            print(f"Error occurred during request: {req_err}")
            return {"error": "Error occurred during weather data request."}

        except KeyError as key_err:
            print(f"Key error in parsing weather data: {key_err}")
            return {"error": "Error parsing weather data."}

# Example usage
# current_weather = WeatherFinder.get_current_weather(47.6062, -122.3321)  # Example for Seattle
# print(current_weather)
