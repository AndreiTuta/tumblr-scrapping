from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import random
import socket
import time
import unicodedata
import urllib
import requests
import zipfile

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from dataclasses import dataclass

@dataclass
class Pin():
    link: str


def randdelay(a, b):
    time.sleep(random.uniform(a, b))


def u_to_s(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore')

class PinterestDownloader():
    def __init__(self):
        print('Initialised image downloader')

    def download(self, image_url, query_param, image_name):
        print(f'Downloading image from {image_url}')
        img_data = requests.get(image_url).content
        path = f'results/{query_param}/{image_name}.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return path

class PinterestHelper(object):
    def __init__(self):
        options = Options()
        options.log.level = "trace"
        options.add_argument("-remote-debugging-port=9224")
        options.add_argument("-headless")
        options.add_argument("-disable-gpu")
        options.add_argument("-no-sandbox")

        options.binary_location = os.environ.get('FIREFOX_BIN')

        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = False
        firefox_driver = webdriver.Firefox(
            capabilities=cap,
            executable_path=os.environ.get('GECKODRIVER_PATH'),
            options=options)
        self.browser = firefox_driver
        # self.login(email, pw)
        self.images = {}
        self.url = 'http://pinterest.com/search/pins/?q='
        
    def set_term(self, term, max):
        self.max = max
        self.query(term)

    def query(self, term):
        tries = 0
        try:
            self.browser.get(self.url + term)
            images = self.process_images(self.max, tries, 500)
            self.images[term] = images
        except (socket.error, socket.timeout):
            pass    

    def close(self):
        """ Closes the browser """
        self.browser.close()

    def process_images(self, max, tries=0, threshold=500):
        results = []
        found = 0
        while threshold > 0:
            print(f'Processing {tries}')
            try:
                images = self.browser.find_elements_by_tag_name("img")
                if tries > threshold - 1: 
                    return results
                for i in images:
                    if found >= max:
                        print(f'Max reached: {found}')
                        return results
                    src = i.get_attribute("src")
                    if src:
                        if src.find("/236x/") != -1 or src.find("/474x/") != 1:
                            print(src)
                            src = src.replace("/236x/", "/736x/")
                            src = src.replace("/474x/", "/736x/")
                            results.append(u_to_s(src))
                            found+=1
                body = self.browser.find_element_by_xpath('/html/body')
                body.send_keys(Keys.PAGE_DOWN)
                randdelay(0, 1)
                tries+=1
            except StaleElementReferenceException:
                tries+=1
        print(f'Processed {len(results)}')
        return results

    def write_results(self, query_param):
        print(f'Saving {len(self.images)} urls to text file')
        if not os.path.exists(f'results/{query_param}'):
            print(f'Creating results/{query_param}')
            os.makedirs(f'results/{query_param}')
        else:
            print(f'Cleaning results/{query_param}')
            for root, dirs, files in os.walk(f'results/{query_param}'):
                for file in files:
                    os.remove(os.path.join(root, file))
            print(f'Cleaned folder of previous results')
        # then download images to file
        self.downloader = PinterestDownloader()
        images = self.images[query_param]
        zip_file = zipfile.ZipFile(f'results/{query_param}/temp.zip', 'w')
        for image in images:
            zip_file.write(self.downloader.download(image, query_param, f'{query_param}-{images.index(image)}'), compress_type=zipfile.ZIP_DEFLATED)
        print(f'Saved {len(self.images)} images')
        zip_file.close()

    def scrap(self, term: str, size: str):
        size_int = 1
        try:
            size_int = int(size)
            print(f'Searching for {size_int}')
        except ValueError:
            # Handle the exception
            print('Not an integer was provided. Defaulting to 10.')
        pins = []
        self.set_term(urllib.parse.quote(term), size_int)
        for image in self.images[term]:
            url = image.decode('UTF-8')
            pins.append(Pin(url))
        print(f'Found {len(pins)} pins')
        self.close()
        return pins
        # ph.write_results(term, ph.images)

def init():
    ph = PinterestHelper()
    return ph
