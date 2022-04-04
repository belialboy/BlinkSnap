import boto3
from botocore.exceptions import ClientError
import logging
import os
import tempfile
import datetime
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logger.info("Underpants!")
    
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    
    s3 = boto3.resource('s3')

    bucket_name = os.environ['outputBucket']

    my_bucket = s3.Bucket(bucket_name)
    
    tmp = "/tmp/image.tmp"
    out = "/tmp/{year}-{week}-output.gif"
    images = []
    
    for my_bucket_object in my_bucket.objects.all():
        looping_week = -1
        if my_bucket_object.key.split(".")[1] == "jpg":
            file_year, file_week_num, file_day_of_week = my_bucket_object.last_modified.isocalendar()
    
            if (file_year == year and file_week_num == week_num):
                logger.info("Reading {} ({})".format(my_bucket_object.key,len(images)+1))
                my_bucket.download_file(my_bucket_object.key, tmp)
                raw_image = Image.open(tmp)
                images.append(raw_image.resize((640,360),reducing_gap=2.0))
                
    logger.info("Got all the images I need for {} week {}".format(year,week_num))
    out_file = out.format(year=year,week=week_num)
    write_out(images,out_file,my_bucket)
    logger.info("Profit!")

def write_out(images,out_filename,bucket_obj):
    primary = images.pop(0)
    primary.save(out_filename, save_all=True, append_images=images, duration=250, loop=0, optimize=True)
    object_name = out_filename.split("/")[-1]
    logger.info("Writing out : {}".format(out_filename))
    bucket_obj.upload_file(out_filename, object_name)
    images = []

if __name__ == "__main__":
    lambda_handler(0,0)
