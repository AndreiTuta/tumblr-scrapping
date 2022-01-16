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

try:
    from config import PINTEREST_PASSWORD, PINTEREST_USERNAME, QUERY_PARAM
except Exception as e:
    print(e)


def randdelay(a, b):
    time.sleep(random.uniform(a, b))


def u_to_s(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore')


class PinterestHelper(object):
    def __init__(self, email, pw):
        self.browser = webdriver.Firefox(executable_path='/usr/bin/geckodriver')
        self.downloader = PinterestDownloader()
        # self.browser = webdriver.Chrome()
        # self.login(email, pw)

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

    def runme(self, url, threshold=500):
        final_results = []
        tries = 0
        try:
            self.browser.get(url)
            final_results.extend(self.process_images(tries, threshold))
        except (socket.error, socket.timeout):
            pass
        return final_results

    def close(self):
        """ Closes the browser """
        self.browser.close()

    def process_images(self,tries=0, threshold=500):
        results = []
        while threshold > 0:
            print(f'Processing {tries}')
            try:
                images = self.browser.find_elements_by_tag_name("img")
                if tries > threshold:
                    return results
                for i in images:
                    src = i.get_attribute("src")
                    if src:
                        if src.find("/236x/") != -1 or src.find("/474x/") != 1:
                            print(src)
                            src = src.replace("/236x/", "/736x/")
                            src = src.replace("/474x/", "/736x/")
                            results.append(u_to_s(src))
                body = self.browser.find_element_by_xpath('/html/body')
                body.send_keys(Keys.PAGE_DOWN)
                randdelay(0, 1)
                tries+=1
            except StaleElementReferenceException:
                tries+=1
        return results

    def write_results(self, query_param, images):
        print(f'Saving {len(images)} urls to text file')
        if not os.path.exists(f'results/{query_param}'):
            print(f'Creating results/{query_param}')
            os.makedirs(f'results/{query_param}')
        # save results in a file
        with open(f'results/{query_param}/'+query_param.replace(" ", "") + "_pins.txt", "w") as file:
            file.write('\n'.join([i.decode('UTF-8') for i in images]))
        # then download images to file
        for image in images:
            self.downloader.download(image, query_param, f'{query_param}-{images.index(image)}')

class PinterestDownloader():
    def __init__(self):
        print('Initialised image downloader')

    def download(self, image_url, query_param, image_name):
        print(f'Downloading image from {image_url}')
        img_data = requests.get(image_url).content
        with open(f'results/{query_param}/{image_name}.jpg', 'wb') as handler:
            handler.write(img_data)



def main():
    term = QUERY_PARAM
    ph = PinterestHelper(PINTEREST_USERNAME, PINTEREST_PASSWORD)
    images = ph.runme('http://pinterest.com/search/pins/?q=' + urllib.parse.quote(term), 10)
    ph.write_results(term, images)
    ph.close()



if __name__ == '__main__':
    main()
