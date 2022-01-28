#Importing the ncessary modules
from logger import Logging
from Cassandra import Cassandra
from helper_module import *
from scrapper import Scrapper

from schedular import Email 
from schedular import TimeClass
from flask import Flask, request, render_template
import requests
import os
import urllib
import time
from selenium import webdriver
import shutil
from selenium.webdriver.common.keys import Keys
import datetime
#from utils import config


#Instantiating log Object
logg_object = Logging()
#Creating the custom based logger in the database
logg_object.create_logger()
#Instantiating Database Object
Cassandra_object = Cassandra()
#Creating a table in the database to store user inputs
Cassandra_object.create_table()
logg_object.print_log("table created in the database to include user entries ","info")


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():

    """
    This function displays home page to the user to submit a request.
    """

    try:
        logg_object.print_log("log is initialized, displaying index.html page for the user to request","info")
        return render_template('index.html')

    except Exception as e:
        logg_object.print_log("Something went wrong while rendering 'index.html","ERROR",e)

@app.route("/show_link", methods=['GET', 'POST'])
def get_image():

    '''This function calls various modules developed within this project to perform the task'''

    try:
        if request.method == 'POST':

            #Storing user information in a variable
            image_name = request.form.get('image_name') #search strings
            num_images = request.form.get('num_images') #number of images that user is interested to download
            email = request.form.get('email') # email id to which URL will be sent to download
            schedule_time = datetime.datetime.strptime(request.form.get('start_timestamp'), '%Y-%m-%dT%H:%M') # time at which the user wants to receive the url

            logg_object.print_log("Recieved user inputs, processing....","info")

            #Instantiating Scrapper object
            scrapper_instance = Scrapper().search_and_download(image_name,num_images) # donwloading images in a folder and zippping them

            #uploading the zip fule to s3 Bucket
            upload_zip_to_s3_instance = S3BucketUpload().s3_upload(image_name) 

            #Fetching the url of zip file from S3 bucket
            retrieve_zip_instance_for_email =UrlRetriveEmail().url_retrive(image_name,email)

            #deleting the zip file after uploading it to S3 bucket
            delete_zip_file_instance = DeleteZipFile().delete_zip(image_name)

            # Retrieve url in an instance to displaying in webpage
            retrieve_zip_instance_for_webpage = UrlRetrive().url_retrive(image_name)

            #Inserting user entries to database
            Cassandra_object.insert_data(str(schedule_time), image_name,num_images,email,retrieve_zip_instance_for_webpage)
            
            
            return '{"aws_region":"ap-south-1","access_key":'+f"{os.environ.get('ACCESS_KEY')}"+',"access_secret":'+f"{os.environ.get('ACCESS_SECRET')}"+',"RECIPIENT":'+f'"{email}"'+',"SENDER":"naveen.i.pujar@gmail.com","url":'+f'"{url}"'+'}'
            email_instance.role()
            email_instance.lambda_function()

            #Converting IST to GMT for schedule cron event
            cron_instance = TimeClass().datetime_to_cron(schedule_time)

            #Scheduling email
            email_instance.Cloudwatch(cron_instance,retrieve_zip_instance_for_email)
            
    except Exception as e:
            logg_object.print_log("Something went wrong in try block of 'get_image()'","ERROR",e)
            #Cassandra_object.shutdown()
            raise Exception(e)
    
    #returning URL to the webpage
    return render_template("result.html", result = retrieve_zip_instance_for_webpage)

if __name__ == '__main__':
    app.run(debug=True)