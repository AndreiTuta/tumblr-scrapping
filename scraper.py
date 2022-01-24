from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import random
import socket
import time
import unicodedata
import urllib
import requests

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from dataclasses import dataclass

try:
    from config import PINTEREST_PASSWORD, PINTEREST_USERNAME, QUERY_PARAM
except Exception as e:
    print(e)


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
        with open(f'results/{query_param}/{image_name}.jpg', 'wb') as handler:
            handler.write(img_data)

class PinterestHelper(object):
    def __init__(self, email, pw, url, max=50):
        self.browser = webdriver.Firefox(executable_path='/usr/bin/geckodriver')
        # self.login(email, pw)
        self.images = []
        tries = 0
        try:
            self.browser.get(url)
            self.images = self.process_images(max, tries, 500)
        except (socket.error, socket.timeout):
            pass

    def login(self, email, pw):
        self.browser.get("https://www.pinterest.com")
        login = self.browser.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[2]/button/div')
        login.click()
        email_elem = self.browser.find_element_by_xpath('//*[@id="email"]')
        email_elem.send_keys(email)
        password_elem = self.browser.find_element_by_name('password')
        password_elem.send_keys(pw)
        password_elem.send_keys(Keys.RETURN)
        randdelay(2, 4)

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

    def write_results(self, query_param, images):
        print(f'Saving {len(images)} urls to text file')
        if not os.path.exists(f'results/{query_param}'):
            print(f'Creating results/{query_param}')
            os.makedirs(f'results/{query_param}')
        else:
            print(f'Cleaning results/{query_param}')
            for root, dirs, files in os.walk(f'results/{query_param}'):
                for file in files:
                    os.remove(os.path.join(root, file))
            print(f'Cleaned folder of previous results')
        # save results in a file
        with open(f'results/{query_param}/'+query_param.replace(" ", "") + "_pins.txt", "w") as file:
            file.write('\n'.join([i.decode('UTF-8') for i in images]))
        # then download images to file
        self.downloader = PinterestDownloader()
        for image in images:
            self.downloader.download(image, query_param, f'{query_param}-{images.index(image)}')
        print(f'Saved {len(images)} images')


def scrap(term: str, size: str):
    pins = []
    size_int = 1
    try:
        size_int = int(size)
        print(f'Searching for {size_int}')
    except ValueError:
        # Handle the exception
        print('Not an integer was provided. Defaulting to 10.')
    ph = PinterestHelper(PINTEREST_USERNAME, PINTEREST_PASSWORD, 'http://pinterest.com/search/pins/?q=' + urllib.parse.quote(term), size_int)
    for image in ph.images:
        url = image.decode('UTF-8')
        pins.append(Pin(url))
    print(f'Found {len(pins)} pins')
    ph.close()
    return pins
    # ph.write_results(term, ph.images)