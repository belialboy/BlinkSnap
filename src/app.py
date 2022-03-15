import json

import boto3
from botocore.exceptions import ClientError

from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load

import logging

import time

import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Underpants!")
    
    blink = authBlink()
    
    s3 = boto3.resource('s3')
    
    # blink.refresh(force=True)
    for name, camera in blink.cameras.items():
        image_data = camera.get_media()       # Take a new picture with the camera
        object_name = "{}-{}.jpg".format(name,int(time.time()))
        object = s3.Object(os.environ['outputBucket'], object_name)
        object.put(Body=image_data)

    logger.info("Profit!")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world"
        }),
    }

def getSSM(ssm,parametername):
    try:
        response = ssm.get_parameter(Name=parametername)
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error("Failed to get {} SSM parameter".format(parametername))
        return False
    
def authBlink():
    
    blink = Blink()
    
    ssm = boto3.client("ssm")
    blink_creds = getSSM(ssm,"BlinkCreds")
    
    if blink_creds is False:
        exit()
    
    auth = Auth(blink_creds)
    blink.auth = auth
    blink.start()
    
    return blink
