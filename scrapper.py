#final scrapper
import os
import time
import requests
from selenium import webdriver
import shutil
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_binary
from helper_module import *
import urllib
from logger import Logging

#Instantiating log Object
logg_object = Logging()
#Creating the custom based logger in the database
logg_object.create_logger()
#Instantiating Database Object


class Scrapper:

    def fetch_image_urls(self, query: str, max_links_to_fetch: int, sleep_between_interactions: int = 1):
        """
        To fetch image urls, which will be later used to download the images
        Parameters
        ----------
        query: search keyword
        max_links_to_fetch: no. of links to be fetched
        sleep_between_interactions: break between 2
        """

        def scroll_to_end():

            """
            To scroll down html page while scraping to load new images
            """

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)

            # build the google query

        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        # load the page
        path = 'chromedriver.exe'
        self.driver = webdriver.Chrome(path)
        self.driver.get(search_url.format(q=query))

        Image_folder1 = query + '_images'
        image_urls = []
        image_count = 0
        results_start = 0

        while int(image_count) < int(max_links_to_fetch):
            scroll_to_end()
            # get all image thumbnail results
            thumbnail_results = self.driver.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)
            logg_object.print_log(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}","INFO")
            
            for img in thumbnail_results[results_start:number_results]:
                # try to click every thumbnail such that we can get the real image behind it
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    continue

                # extract image urls
                actual_images = self.driver.find_elements_by_css_selector("img.n3VNCb")
                for actual_image in actual_images:
                    if actual_image.get_attribute(
                        "src"
                    ) and "http" in actual_image.get_attribute("src"):
                        image_urls.append(actual_image.get_attribute("src"))

                image_count = len(image_urls)

                if len(image_urls) >= int(max_links_to_fetch):
                    logg_object.print_log(f"Found: {len(image_urls)} image links, done!","INFO")
                    break
            else:
                logg_object.print_log(f"Found: {len(image_urls)} image links, looking for more ...","INFO")
                time.sleep(30)
                return
                load_more_button = wd.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")

            # move the result startpoint further down
            results_start = len(thumbnail_results)

        return image_urls
    
    def persist_image(self, folder_path: str, url: str, counter):

        """
        To save images
        Parameters
        ----------
        folder_path: target folder
        url:image url
        counter:image counter
        """
        
        try:
            image_content = requests.get(url).content

        except Exception as e:
            logg_object.print_log(f"Could not download {url} - {str(e)}","EROOR",e)


        try:
            f = open(
                os.path.join(folder_path, "jpg" + "_" + str(counter) + ".jpg"), "wb"
            )
            f.write(image_content)
            f.close()
            logg_object.print_log(f"SUCCESS - saved {url} - as {folder_path}","INFO")

        except Exception as e:
            logg_object.print_log(f"Could not save {url} - {str(e)}","EROOR",e)


    def search_and_download(self, name, count):

        """
        To scroll down html page while scraping to load new images
        """

        Image_folder1 = name + '_images'
        res = self.fetch_image_urls(name, count, sleep_between_interactions=0.5)

        new_folder_instance = CreateFolder()
        new_folder_instance.make_folder(name)

        counter = 0
        for elem in res:
            logg_object.print_log( "Download Started","info")
            self.persist_image(Image_folder1, elem, counter)
            counter += 1

        logg_object.print_log(f"extracted '{counter} images' -extraction completed","INFO")

        create_archive_instance = Createarchive().make_archive(name)
        logg_object.print_log("Folder zipped","INFO")

        delete_folder_instance = DeleteFolder().delete_folder(name)
        logg_object.print_log("Folder deleted","INFO")








