import boto3
import json
import os
from botocore.exceptions import BotoCoreError, ClientError

class CoordinatesFinder:
    @staticmethod
    def get_coordinates(place_name):
        # Using environment variables for configuration
        place_index_name = os.environ.get('PLACE_INDEX_NAME')

        # Initialize the Amazon Location Service client
        location = boto3.client("location")
        
        try:
            result = location.search_place_index_for_text(
                IndexName=place_index_name,
                Text=place_name,
                MaxResults=1
            )
            print(json.dumps(result, indent=4))

            point = result['Results'][0]['Place']['Geometry']['Point']
            return {"longitude": point[0], "latitude": point[1]}
        
        except (KeyError, TypeError, IndexError) as e:
            print(f"Error accessing location data: {e}")
            return {"error": "There was an error getting the location."}
        
        except (BotoCoreError, ClientError) as error:
            print(f"Error communicating with AWS services: {error}")
            return {"error": "There was an error communicating with AWS services."}

# Example usage
# coordinates = CoordinatesFinder.get_coordinates("Seattle")
# print(coordinates)