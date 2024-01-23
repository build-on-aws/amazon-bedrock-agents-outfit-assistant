# Amazon Bedrock Agent Demo 
## Outfit Assistant 

![What should I wear today?](/images/illustration-of-different-weather-and-outfits.png)
*Source: Titan Image Generator G1 - 'illustration of different weather and outfits'*

    Level 300: The following information and instructions are provided at 300 level.  Some experience deploying solutions on Amazon Web Services is required, including working with Amazon Lambda functions.

Note: The demo relies on you having an account with OpenWeatherMap, and an API key to access the [Weather](https://openweathermap.org/current) service.  This service is available on the OpenWeatherMap free plan. Please review any license terms applicable to the service with your legal team and confirm that your use case complies with the terms before proceeding.

## Introduction

This repo contains code for a demo of Amazon Bedrock Agents. 

In this demo, you will deploy an agent that is able to assist you in selecting the ideal outfit to where given your location.  

In a standard deployment, a Large Language Model (LLM) can only reference 'knowledge' that it obtained during training.  As such, when prompted to generate up-to-date information such as the current date and time, or getting the weather conditions, the model is left with no alternative other than to hallucinate.  

In this demo, you will use Amazon Bedrock Agents to create a solution that enables an LLM to leverage realtime information including the date, time, and weather information. The solution will use this information to make suggestions for what outfit to wear.

This architecture could be easily extended to work with any number of APIs or data sources.  If you are able to connect to your data from an Amazon Lambda function, then it can be used with Amazon Bedrock Agents. 

![Outfit Assistant Architecture Diagram](/images/outfit-assistant-diag-1.png)

## Amazon Location Service

Within this demo, the Lambda function you will deploy uses Amazon Location Service to lookup the location of place names, and the find the time zone for a given location.

For more information about Amazon Location Service see here: https://aws.amazon.com/location/

To enable Amazon Location Service:

1. Log in to the AWS console within the region you are deploying too (Recommended us-west-2 for demo purposes.) and navigate to Amazon Location Service.
1. From the left hand menu, select `Place indexes`.
1. If you have an index listed with a `Data provider` of `HERE`, then you use this if you wish, just take a note of the `Name` of the index.
1. If you do not have a suitable index, then select `Create place index`, provide a name for the index (make a note of this for later), and select `HERE` as the `Data provider`. 
1. Leave all other values as default and select `Create place index`.

(The name of the index will be set as a value for an environment variable for the Lambda function.)

## Lambda Function

The code required for the Lambda Function is in `./lambda_src`. All the files in this folder need to be uploaded to the Lambda function, this includes the main `lambda_function.py` as well as three class files that are used to perform the actions of the service: `coordinates_finder.py`, `time_finder.py`, and `weather_finder.py`.

(A simple way to deploy the code, is to zip these files together and upload via the AWS console.)

The function was developed and tested with: 
- Python 3.12
- Memory 128MB
- Timeout 3 seconds

### Environment Variables

The Lambda function requires two environment variables to be set as follows: 

- PLACE_INDEX_NAME: The name of the place index resource in Amazon Location Service 
  used for fetching coordinates and time. Example: 'explore.place.Here'
- OPENWEATHER_API_KEY: API key for OpenWeatherMap to fetch weather information. Make sure to obtain this key by registering at https://openweathermap.org/api 

### Permissions

The Lambda function requires both a policy with permissions to call other services, and a resource policy to allow it to be called by the Amazon Bedrock agent.

#### Policy for IAM role:

It's recommended to attach the standard Lambda execution policy to allow for logging etc.  In addition a policy similar to this is required for access to the Location service:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"geo:SearchPlaceIndexForText",
				"geo:SearchPlaceIndexForPosition"
			],
			"Resource": "arn:aws:geo:*:[YOUR_ACCOUNT_ID]:place-index/*"
		}
	]
}
```

#### Lambda resource policy:

The following role must be set as the resource policy for the Lambda function. This allows the function to be called by the Amazon Bedrock Agent: 

```json
{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "amazon-bedrock-agent",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-west-2:[YOUR_ACCOUNT_ID]:function:agent_location_services",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:bedrock:us-west-2:[YOUR_ACCOUNT_ID]:agent/[YOUR_AGENT_ID]"
        }
      }
    }
  ]
}
```



### Lambda Layer

The Lambda function is dependant on some Python libraries.  These libraries can be deployed to Lambda as a Lambda Layer.  If you are using a deployment process such as SAM, you can use a `requirements.txt` file as follows:

```txt
pytz==2023.3
numpy==1.26.0
requests==2.31.0
```

If you are deploying the code through the console and want a quick and easy way to create the layers, you can follow the following steps.  (Note, I recommend creating separate layers for each dependency to help avoid individual size limit issues.) 

From the AWS Console open AWS CloudShell.  (https://aws.amazon.com/blogs/aws/aws-cloudshell-command-line-access-to-aws-resources/)

Adjust the following code to create layers as for each dependency. Adjust the folder names, what you install via pip3 and the layer name as needed. 

```bash
mkdir ./my-layer
cd ./my-layer
mkdir ./python
pip3 install -t ./python/ requests==2.31.0
zip -r ../my-layer.zip .
cd ..

aws lambda publish-layer-version \
--layer-name my-layer \
--zip-file fileb://my-layer.zip
```

### Testing the Lambda function

To test the Lambda function without having to create an agent first, or simply to test without having to invoke the agent, I have provided you with three test event JSON files that can be pasted into the test event configuration page within the Lambda function.  Each test event is formatted as the event will be sent from the agent:

- `./tests/lambda_event_location.json`
- `./tests/lambda_event_time.json`
- `./tests/lambda__event_weather.json`

## Create an Amazon Bedrock Agent

Before following these steps, you will need: 
- The name of the Lambda function deployed with the code included in this repo. 
- The contents of `agent_instructions.txt` and `openAPI_schema.json` ready to copy and paste. 

To deploy the solution in to Amazon Bedrock, follow these steps: 

1. Log in to the AWS console and navigate to `Amazon Bedrock`
1. From the left hand menu select `Model access` and ensure that you have access to `anthropic.claude-instant-v1`.
1. From the left hand menu select `Agents` and select `Create agent`
1. Enter an agent name and a description so it's clear what this agent does.
1. For `User input` leave this as `Yes`.
1. For `IAM Permissions` leave this as `Create and use a new service role`.
1. For `Idle session timeout` leave this as `30` minutes.
1. Add tags as you wish, then select `Next`.
1. For the model, select `Anthropic` and `Claude V1` (you can experiment with this selection, you can also update it later).
1. In the `Instructions for the Agent` paste in the contents of `agent_instructions.txt`.  This will form part of the prompt to the LLM, so what is said here matters.  (you can experiment with this selection, you can also update it later). Select `Next`.
1. We are going to skip creating the Action groups now, so under `Add Action groups` select `Delete`, then `Next`.
1. This demo does not use Knowledge base so select `Delete`, then `Next`.
1. Review the details and select `Create Agent`
1. We will now add the action group.  We skipped this earlier as at the time of writing the workflow to add the action group later has more options. 
1. Scroll to `Working draft` and select the name `Working draft`.
1. Under `Action groups` select `Add`.  Give the action group a name and description so it's clear what this agent does. From the `Select Lambda function` selection box, select the Lambda function you deployed.  If you do not see your deployed function here, then make sure it is deployed to the region you are working in.  Select `$LATEST` for the function version. Under `Select API schema` choose `Define with in-line OpenAPI schema editor`.  In the editor that appears, clear out all the existing text, and replace it with the contents of `openAPI_schema.json`. Now select `Add`.

At this point your agent should be ready for testing.  To test the agent: 

1. With the agent selected in the console, select `Prepare`, and when this is complete, select `Test`. 
1. A chat window will appear on the right hand side.  You can now chat with your agent. Here are some messages you can try, note that they don't have to be limited to what outfit to wear: 
    - "I am in Brisbane Australia, what should I wear today?"
    - "What is the time?" (May ask you where you are if this is the first message.)
    - "Is it raining in Oslo?"

If you are happy with the performance of the agent, you can deploy it, and access it via your own application.

1. With the agent selected in the console, select `Create Alias`, enter a name and description so it's clear at what point in its development it was deployed, and select `Create Alias`.   
1. To call this agent alias from your own code you will need the agent ID which is shown in the `Agent overview` section of the console, and the alias ID which is shown in the `Aliases` section towards the bottom of the agent console page. Note that these IDs are generated by the service, and are not the same as the names you used.
1. There is sample Python code for invoking your agent in a notebook `./test/agent_test.ipynb`.  For more information on the Agents for Amazon Bedrock API see here: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-api.html and for Python see here: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

