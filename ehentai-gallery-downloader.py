#!/usr/bin/env python3

"""
TODO:
* Parse number of images from main gallery page
* Allow user to supply gallery URLs as an args. If args are present,
then skip prompting the user to enter a URL.
* Allow user to download multiple galleries.
** Refactor how the user is presented with information regarding
a given gallery. Notify them of the gallery's title and the number of images
the gallery contains.
NOTES:
* Will we be timed out for making to many consecutive requests? Hasn't
happened yet.
"""

from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlparse
from html.parser import HTMLParser
from os import mkdir
import re


class GalleryParser(HTMLParser):
    # This class parses out individual page URLs from a given
    # gallery and feeds each URL to the GalleryPageParser.
    def __init__(self):
        HTMLParser.__init__(self)
        self.found_title = False
        self.title_saved = False
        self.page_parser = GalleryPageParser()
        self.page_urls = {gallery_url}
        # we have to put the individual page links in a set
        # because they appear multiple times in a gallery.

    def feed_page_parser(self):
        for url in self.page_urls:
            self.page_parser.feed(urlopen(url).read().decode())

    def is_page_url(url):
        pattern = "^http[s]?:\/\/g.e-hentai.org\/g\/[0-9]+\/[0-9a-z]+\/\?p=[0-9]+$"
        if re.match(pattern, url):
            return True

    def handle_data(self, data):
        if self.found_title and not self.title_saved:
            global save_folder
            save_folder = data[:-21]
            # remove trailing " - E-Hentai Galleries". This may be
            # prone to errors in the future.
            try:
                mkdir(save_folder)
            except FileExistsError:
                pass
            self.title_saved = True
            save_folder += "/"

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.found_title = True
        if tag != 'a':
            return
        if attrs[0][0] == 'href' and GalleryParser.is_page_url(attrs[0][1]):
            self.page_urls.add(attrs[0][1])


class GalleryPageParser(HTMLParser):
    # For individual pages of galleries.
    def __init__(self):
        HTMLParser.__init__(self)
        self.image_parser = ImageParser()
    
    def is_img_url(url):
        pattern = "^http[s]?:\/\/g.e-hentai.org\/s\/[0-9a-zA-Z]+\/[0-9]+-[0-9]+$"
        if re.match(pattern,url):
            return True

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        if attrs[0][0] == 'href' and GalleryPageParser.is_img_url(attrs[0][1]):
            self.image_parser.feed(urlopen(attrs[0][1]).read().decode())


class ImageParser(HTMLParser):
    # This class parses the HTML of the image URL a hotlink, and downloads
    # said image.
    def __init__(self):
        HTMLParser.__init__(self)
        self.downloaded_images = 0

    def get_savename(url):
        return urlparse(url)[2].split('/')[-1]

    def is_raw_img_url(url):
        ip_addr_pattern = "^([0-9]{1,3}.){3}[0-9]{1,3}(:[0-9]{1,5})?$"
        url = urlparse(url)[1]
        if re.match(ip_addr_pattern, url):
            return True

    def handle_starttag(self, tag, attrs):
        if tag != 'img':
            return
        if ImageParser.is_raw_img_url(attrs[0][1]):
            global downloaded_images
            downloaded_images += 1
            self.raw_img_url = attrs[0][1]
            self.save_name= ImageParser.get_savename(self.raw_img_url)
            print("Page %d of ?:" % self.downloaded_images)
            # TODO: Fix this^ print statement and actually tell the user
            # how many pages the gallery contains.
            print(self.save_name + "\n")
            urlretrieve(self.raw_img_url, save_folder + self.save_name)

save_folder = ""

gallery_url = input("Enter the URL of the gallery you would like to download: ")
gallery_url = urlparse(gallery_url)
gallery_url = gallery_url[0] + "://" + ''.join(gallery_url[1:3])

downloaded_images = 0
gallery_parser = GalleryParser()

gallery_parser.feed(urlopen(gallery_url).read().decode())
gallery_parser.feed_page_parser()
print("Downloaded %d images" % downloaded_images)