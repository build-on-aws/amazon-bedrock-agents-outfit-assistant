"""
Lambda Function for Location-Based Services
-------------------------------------------

This Lambda function is designed to the Amazon Bedrock Agents specification.

For more details see here: 
https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html 

The function provides several location-based services such as fetching coordinates, 
current time, and weather information for a given place. It relies on external services 
like Amazon Location Service and OpenWeatherMap API.

Environment Variables:
- PLACE_INDEX_NAME: The name of the place index resource in Amazon Location Service 
  used for fetching coordinates and time. Example: 'explore.place.Here'
- OPENWEATHER_API_KEY: API key for OpenWeatherMap to fetch weather information. 
  Make sure to obtain this key by registering at https://openweathermap.org/api

The Lambda function handles three main API paths:
1. /getCoordinates: Returns the longitude and latitude for a given place name.
2. /getCurrentTime: Provides the current local time for given latitude and longitude.
3. /getCurrentWeather: Retrieves the current weather information for a given latitude and longitude.

Usage:
- To use this Lambda function, the client should send an event with 'apiPath' and 
  necessary 'parameters'.
- The function returns the requested information in JSON format.

Author: Mike Chambers - Developer Advocate Specialist - Amazon Web Services
Date: 2024/01/22
"""

import json
from coordinates_finder import CoordinatesFinder
from time_finder import TimeFinder
from weather_finder import WeatherFinder

def lambda_handler(event, context):
    print(event)
    
    api_path = event['apiPath']
    parameters = {param['name']: param['value'] for param in event['parameters']}

    response_body = handle_request(api_path, parameters)

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': api_path,
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': {'application/json': {'body': json.dumps(response_body)}}
    }

    session_attributes = event.get('sessionAttributes', {})
    prompt_session_attributes = event.get('promptSessionAttributes', {})

    return {
        'messageVersion': '1.0',
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

def handle_request(api_path, parameters):
    if api_path == "/getCoordinates":
        return CoordinatesFinder.get_coordinates(parameters.get('placeName'))
    elif api_path == "/getCurrentTime":
        return TimeFinder.get_current_time(parameters.get('latitude'), parameters.get('longitude'))
    elif api_path == "/getCurrentWeather":
        return WeatherFinder.get_current_weather(parameters.get('latitude'), parameters.get('longitude'))
    else:
        return {"error": "Invalid API path"}
