import os
import json
import boto3
from slaves import *

def lambda_handler(event, context):
	try:
	    send_new_word_via_email()
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
