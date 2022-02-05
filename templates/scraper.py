import json
import pytumblr
import requests
import calendar
import time
import os
import pprint
import zipfile

from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class Post():
    link: str

class TumblrDownloader():
    def __init__(self):
        print('Initialised image downloader')

    def download(self, image_url, query_param, image_name):
        print(f'Downloading image from {image_url}')
        img_data = requests.get(image_url).content
        path = f'results/{query_param}/{image_name}.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return path

class TumblrHelper(object):
    def __init__(self):
        self.api  = pytumblr.TumblrRestClient(
                os.environ.get("TUMBLR_CONSUMER"),
                os.environ.get("TUMBLR_CONSUMER_SECRET"),
                os.environ.get("TUMBLR_TOKEN"),
                os.environ.get("TUMBLR_TOKEN_SECRET")
                )
        self.images={}

    def query(self, term, max):
        images = self.process_images(max, term)
        self.images[term] = list(images)
        return self.images[term]

    def query_tag(self, tag, max):
        # return jsonResp
        return self.api.tagged(tag, filter=filter, limit=max)

    def process_images(self, max, tag):
        filter = 'raw'
        # before = calendar.timegm(time.gmtime())
        results = {}
        max= int(max)
        #Run the tag search and snag the results
        searchResults = self.query_tag(tag, max)
        j = 0
        print(f"{(len(searchResults))} results retreived: {searchResults}")
        for i in searchResults:
            post_tags = (i)['tags']
            for rel_tag in post_tags:
                if tag in rel_tag and rel_tag != tag:
                    print(rel_tag)
                    related_posts = self.query_tag(rel_tag, 1)
                    for post in related_posts:
                        try:
                            url = (post)['post_url']
                        except:
                            url = "Couldn't Get url"
                        try:
                            body = (post)['body']
                            soup_body = BeautifulSoup(body, 'html.parser')
                            img = soup_body.find_all('img')[0]
                            img_source = img['src']
                            results[url]= (Post(img_source))
                        except:
                            body = "Couldn't Get Post Body"
                        print(f'Adding new Post {url}:{j}/{max}')

        return results.values()

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
        self.downloader = TumblrDownloader()
        images = self.images[query_param]
        zip_file = zipfile.ZipFile(f'results/{query_param}/temp.zip', 'w')
        for image in images:
            zip_file.write(self.downloader.download(image.link, query_param, f'{query_param}-{images.index(image)}'), compress_type=zipfile.ZIP_DEFLATED)
        print(f'Saved {len(self.images)} images')
        zip_file.close()


def init():
    ph = TumblrHelper()
    return ph
