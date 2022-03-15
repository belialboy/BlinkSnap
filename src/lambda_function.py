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
    s3 = boto3.client("s3")
    
    for name, camera in blink.cameras.items():
        camera.snap_picture()       # Take a new picture with the camera
        blink.refresh()
        image = camera.get_media()
        if image is None or image.status_code != 200:
            logger.error("Failed to get the image")
            exit()
        
        object_name = "{}-{}.jpg".format(name,int(time.time()))
        object = s3.Object(os.environ['outputBucket'], object_name)
        object.put(Body=image.raw)

    logger.info("Profit!")

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
    
    json_creds = json.loads(blink_creds.replace("'","\""))

    auth = Auth(json_creds)
    blink.auth = auth
    blink.start()
    
    return blink
    
if __name__ == "__main__":
    lambda_handler(0,0)
