import os
import json
import boto3
from helpers import *

def lambda_handler(event, context):
	try:
	    notify_via_email()
	    return {
	        'statusCode': 200,
	        'body': json.dumps('Daily word sent.')
	    }
	except Exception as err:
		return {
	        'statusCode': 404,
	        'body': json.dumps(f'There was an error: {err}')
	    }
	
if __name__ == "__main__":   
    lambda_handler('', '')
