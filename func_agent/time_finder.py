import boto3
import os
import pytz
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

class TimeFinder:
    @staticmethod
    def get_current_time(latitude, longitude):
        # Using environment variables for configuration
        place_index_name = os.environ.get('PLACE_INDEX_NAME')

        # Initialize the Amazon Location Service client
        location = boto3.client("location")

        try:
            result = location.search_place_index_for_position(
                IndexName=place_index_name,
                MaxResults=1,
                Position=[float(longitude), float(latitude)]
            )

            timezone_str = result['Results'][0]['Place']['TimeZone']['Name']
            timezone = pytz.timezone(timezone_str)
            local_time = datetime.now(timezone)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")

        except (KeyError, TypeError, IndexError) as e:
            print(f"Error accessing time data: {e}")
            return {"error": "There was an error getting the time."}

        except (BotoCoreError, ClientError) as error:
            print(f"Error communicating with AWS services: {error}")
            return {"error": "There was an error communicating with AWS services."}

# Example usage
# current_time = TimeFinder.get_current_time(47.6062, -122.3321)  # Example for Seattle
# print(current_time)
