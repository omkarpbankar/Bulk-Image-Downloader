# importing the necessary libraries
import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from logger import Logging
#from utils import config
import os

#Instantiating log Object
logg_object = Logging()
#Creating the custom based logger in the database
logg_object.create_logger()


class Cassandra:

    def __init__(self):

        """
        This function will instantiate the Cassandra driver for storing the data in the database.
        """
        
        try:

            cloud_config= {'secure_connect_bundle': 'secure-connect-bulk-image-downloader.zip'}
            auth_provider = PlainTextAuthProvider(os.environ.get('CLIENT_ID'),os.environ.get('CLIENT_SECRET'))
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = cluster.connect('aidboto')
            row = self.session.execute("select release_version from system.local").one()
            if row:
                logg_object.print_log(f"row[0]","INFO")
                
            else:
                logg_object.print_log("An error occurred","ERROR")


        except Exception as e:
            logg_object.print_log("Someting went wrong in Class Cassandra.__init__","ERROR",e)
            print(e)


    def create_table(self):
    
        """
        This function will create the table in the database.
        """
        
        try:
            qry ="CREATE TABLE IF NOT EXISTS aidboto.userdata(schedule_time TEXT, search_term TEXT,no_images TEXT,email_id TEXT, zip_instance_web TEXT, PRIMARY KEY(email_id));"
            self.session.execute(qry)
            
        except Exception as e:
            logg_object.print_log("Someting went wrong in Class Cassandra.create_table","ERROR".e)
            print(e)


    def insert_data(self,schedule_time,search_term,no_images,email_id,zip_instance_web):
        
        """
        This function will insert the data into the table.
        param schedule_time: time at which user would want to get the email with the url
        param search_tearm: search string of the image
        param no_images: number of images that the user wants to download
        param email_id: email id to which the user is going to recieve the email with the url
        param zip_instance_web: actual url to download the images
        """
        
        try:
            qry = "INSERT INTO aidboto.userdata (schedule_time,search_term,no_images,email_id,zip_instance_web) VALUES (%s,%s,%s,%s,%s);"
            self.session.execute(qry,[schedule_time,search_term,no_images,email_id,zip_instance_web])
            
        except Exception as e:
            logg_object.print_log("Someting went wrong in Class Cassandra.insert_data","ERROR".e)
            print(e)

        except cassandra.cluster.NoHostAvailable as cluster_error:
            logg_object.print_log("Someting went wrong in Class Cassandra.insert_data","ERROR".e)
            pass
            

    def shutdown(self):
            
            """
            This function will close the session.
            """
            
            try:
                self.session.shutdown()
                
            except Exception as e:
                logg_object.print_log("Someting went wrong in Class Cassandra.shutdown","ERROR".e)
                