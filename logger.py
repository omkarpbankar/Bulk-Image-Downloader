import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
#from utils import config
import os




class Logging:


    def __init__(self):

        """ 
        This function will instantiate the session for the Logger by connecting to database.

        """
        try:

            cloud_config= {'secure_connect_bundle': "secure-connect-bulk-image-downloader.zip"}
            auth_provider = PlainTextAuthProvider(os.environ.get('CLIENT_ID'),os.environ.get('CLIENT_SECRET'))
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = cluster.connect('aidboto')

            row = self.session.execute("select release_version from system.local").one()
            if row:
                print(row[0])
            else:
                print("An error occurred while connecting to Cassandra.Logging__init__.")

        except Exception as e:
            raise Exception(e) 


    def create_logger(self):

        """
        This function will create the logger table in the database.

        """
        try:
            
            qry = "CREATE TABLE IF NOT EXISTS aidboto.logger (log_time TIMESTAMP, log_level TEXT, log_message TEXT, exception TEXT, PRIMARY KEY(log_time,log_level));"
            self.session.execute(qry)
            

        except Exception as e:
            raise Exception(e)

    def print_log(self,log_message, log_level,exception=None):
    
        """
        This function will insert the log message into the logger table.

        """
        try:
            qry = "INSERT INTO aidboto.logger (log_time, log_level, log_message, exception) VALUES (toTimeStamp(toDate(now())), %s, %s, %s);"
            self.session.execute(qry, [log_level, log_message, exception])
            

        except Exception as e:
            raise Exception(e)
        

