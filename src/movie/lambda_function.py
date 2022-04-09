import boto3
from botocore.exceptions import ClientError
import logging
import os
import datetime
from PIL import Image
from PIL import ImageDraw
from twython import Twython

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logger.info("Underpants!")
    
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    print(os.system("ls /opt/ > /tmp/ls.txt"))
    file = open("/tmp/ls.txt", 'rb')
    print(file.read())
    s3 = boto3.resource('s3')
    bucket_name = os.environ['outputBucket']

    my_bucket = s3.Bucket(bucket_name)
    
    tmp = "/tmp/{index}.tmp"
    out = "/tmp/{year}-{week}-output.mp4"
    images = []
    
    for my_bucket_object in my_bucket.objects.all():
        if my_bucket_object.key.split(".")[1] == "jpg":
            file_year, file_week_num, file_day_of_week = my_bucket_object.last_modified.isocalendar()
    
            if (file_year == year and file_week_num == week_num):
                logger.info("Reading {} ({})".format(my_bucket_object.key,len(images)+1))
                my_bucket.download_file(my_bucket_object.key, tmp)
                logger.info("Creating Image object from downloaded file")
                raw_image = Image.open(tmp)
                logger.info("Resizing file to more managable dimensions")
                resized = raw_image.resize((426,240),reducing_gap=2.0)
                ImageDraw.Draw(resized).text((0, 0), my_bucket_object.last_modified.strftime("%A"), (0, 0, 0))
                images.append(resized)
                
    logger.info("Got all the images I need for {} week {}".format(year,week_num))
    out_file = out.format(year=year,week=week_num)
    #write_out(images,out_file,my_bucket)
    os.system("/opt/bin/ffmpeg -framerate 2 -pattern_type glob -i '{infiles}' \ -c:v libx264 -pix_fmt yuv420p {outfile}".format(infiles=tmp.format(index="*"),outfile=out_file))
    
    logger.info("Creating a twitter client")
    twitter = Twython(os.environ["twitterConsumerKey"], 
        os.environ["twitterConsumerSecret"],
        os.environ["twitterAccessTokenKey"], 
        os.environ["twitterAccessTokenSecret"])
    
    logger.info("Opening the gif as a stream")
    twitter_image_filestream = open(out_file, 'rb')
    logger.info("Uploading to twitter")
    twitter_image = twitter.upload_media(media=twitter_image_filestream)
    logger.info("Setting the status")
    twitter.update_status(status="Week {week}/20 of the coachhouse rebuild project. @JarraldM".format(week=week_num-13), media_ids=[twitter_image['media_id']])
    
    logger.info("Profit!")

def write_out(images,out_filename,bucket_obj):
    primary = images.pop(0)
    primary.save(out_filename, save_all=True, append_images=images, duration=250, loop=0, optimize=True)
    object_name = out_filename.split("/")[-1]
    logger.info("Writing out : {}".format(out_filename))
    bucket_obj.upload_file(out_filename, object_name)
    images = []
    return out_filename

if __name__ == "__main__":
    lambda_handler(0,0)
