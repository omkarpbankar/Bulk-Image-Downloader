import os
import urllib
import time

from selenium import webdriver
import shutil
from boto3.session import Session
import boto3
from logger import Logging
#from utils import config

#Instantiating log Object
logg_object = Logging()
#Creating the custom based logger in the database
logg_object.create_logger()


class CreateFolder:
    '''This method takes search string inserted by the user to create folder and archive folder'''

    try:
        def make_folder(self, image_name):

            Image_folder = image_name + '_images'

            if not os.path.exists(Image_folder):
                os.mkdir(Image_folder)
                logg_object.print_log(f'Folder {Image_folder} created successfully','info')
    except Exception as e:
        logg_object.print_log('helper_module.py(CreateFolder)- Something went wrong ' + str(e), 'error')
        raise Exception(e)

class Createarchive:

    def make_archive(self, image_name):
        try:
            Image_folder = image_name + '_images'

            path = os.getcwd() + '\\' + Image_folder

            shutil.make_archive(path, 'zip', Image_folder)
            logg_object.print_log(f'folder {path} ---- archived successfully','info')
        except Exception as e:
            logg_object.print_log('helper_module.py(Createarchive)- Something went wrong ' + str(e), 'error')
            raise Exception(e)

class DeleteFolder:

    def delete_folder(self, image_name):
        try:
            Image_folder = image_name + '_images'

            shutil.rmtree(Image_folder)
            logg_object.print_log(f'folder {Image_folder} deleted successfully','info')
        except Exception as e:
            logg_object.print_log('helper_module.py(DeleteFolder)- Something went wrong ' + str(e), 'error')
            raise Exception(e)

class DeleteZipFile:

    def delete_zip(self, image_name):
        try:
            Zip_file = image_name + '_images.zip'

            os.remove(Zip_file)
            logg_object.print_log(f'Zip_file {Zip_file} deleted successfully','info')
        except Exception as e:
            logg_object.print_log('helper_module.py(DeleteZipFile)- Something went wrong ' + str(e), 'error')
            raise Exception(e)

class S3BucketUpload:

    def __init__(self):
        pass

    def s3_upload(self, Image_name):
        try:
            obj = Image_name + '_images' + '.zip'

            ACCESS_KEY_ID = os.environ.get('ACCESS_KEY')
            SECRET_KEY = os.environ.get('ACCESS_SECRET')

            session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_KEY)

            s3 = session.resource('s3')

            bucket_name = 'aidboto'

            path = os.getcwd() + '\\' + obj

            s3.meta.client.upload_file(path, bucket_name, obj)

            logg_object.print_log('Sucessfully uploaded to s3 bucket','info')
        except Exception as e:
            logg_object.print_log('helper_module.py(S3BucketUpload)- Something went wrong ' + str(e), 'error')
            raise Exception(e)


class UrlRetriveEmail:

    def __init__(self):
        pass

    def url_retrive(sel, Image_name, email):

        try:
            obj = Image_name + '_images' + '.zip'

            from boto3 import Session


            ACCESS_KEY_ID = os.environ.get('ACCESS_KEY')
            SECRET_KEY = os.environ.get('ACCESS_SECRET')

            REGION_NAME = "ap-south-1"
            BUCKET_NAME = 'aidboto'

            ses = Session(aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=SECRET_KEY,
                      region_name=REGION_NAME)
            client = ses.client('s3')

            key = obj

            url = client.generate_presigned_url(
              ClientMethod='get_object',
              Params={
                     'Bucket': BUCKET_NAME,
                     'Key': key,
                     'ResponseContentDisposition': 'attachment'
                     },
                     ExpiresIn=600000
              )

            logg_object.print_log('got the url of the images','info')
            return '{"aws_region":"ap-south-1","access_key":'+f"{os.environ.get('ACCESS_KEY')}"+',"access_secret":'+f"{os.environ.get('ACCESS_SECRET')}"+',"RECIPIENT":'+f'"{email}"'+',"SENDER":"naveen.i.pujar@gmail.com","url":'+f'"{url}"'+'}'
            
        except Exception as e:
            logg_object.print_log('helper_module.py(UrlRetrive)- Something went wrong ' + str(e), 'error')
            raise Exception(e)

class UrlRetrive:

    def __init__(self):
        pass

    def url_retrive(sel, Image_name):

        try:
            obj = Image_name + '_images' + '.zip'

            from boto3 import Session


            ACCESS_KEY = os.environ.get('ACCESS_KEY')
            
            SECRET_KEY = os.environ.get('ACCESS_SECRET')

            REGION_NAME = "ap-south-1"
            BUCKET_NAME = 'aidboto'

            ses = Session(aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      region_name=REGION_NAME)
            client = ses.client('s3')

            key = obj

            url = client.generate_presigned_url(
              ClientMethod='get_object',
              Params={
                     'Bucket': BUCKET_NAME,
                     'Key': key,
                     'ResponseContentDisposition': 'attachment'
                     },
                     ExpiresIn=600000
              )

            #return url
            return url
        except Exception as e:
            logg_object.print_log('helper_module.py(UrlRetrive)- Something went wrong ' + str(e), 'error')
            raise Exception(e)
