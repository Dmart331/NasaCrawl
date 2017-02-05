#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
*********************************************
 Nasa's picture of the day since 1995. 
 For Python 3 + by Drew martin
*********************************************

 Saves all pictures from Nasa's picture of the day archive to the current directory.
"""

import os
import lxml
import pickle 
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from clint.textui import progress, puts, colored

html = 'http://apod.nasa.gov/apod/'

def load():
    puts("Loading archive...")
    url = 'http://apod.nasa.gov/apod/'
    request = Request(url)
    data = urlopen(request).read()
    puts("Opening archive...")
    soup = BeautifulSoup(data, 'lxml')
    results = soup.find('b').findAll('a')
    for result in progress.bar(results):
        url.append(result['href'])
    puts(colored.green("Found %d links." % len(url)))
    return url

def getPhotos(url, thumbs=False):
    puts("Locating Photos...")
    photos = {}
    typeErrorCount = 0
    keyErrorCount = 0
    urlErrorCount = 0
    for url in progress.bar(url):
        try:
            data = urlopen(html)
            soup = BeautifulSoup(data, 'lxml')
            result = soup.find('img')
            if (result is None):
                typeErrorCount += 1
                continue
                if (thumbs):
                    photos[url] = result['src']
            else:
                photos[url] = result.parent['href']
        except TypeError:
            typeErrorCount += 1
        except KeyError:
            keyErrorCount += 1
        
    puts(colored.green("Found %d photos." % len(photos.values())))
    puts(colored.red("URL Error Count: %d" % urlErrorCount))
    puts(colored.red("Key Error Count: %d" % keyErrorCount))
    puts(colored.red("Type Error Count: %d" % typeErrorCount))
    with open('photos.pkl', 'wb') as output:
        pickle.dump(photos, output, pickle.HIGHEST_PROTOCOL)
    return photos


def downloadPhoto(folder, photo):
    try:
        u = urlopen(photo)
        localFile = open(os.path.join(folder, photo.split('/')[-1]), "wb")
        localFile.write(u.read())
        localFile.close()
        u.close()
    except urlopen.HTTPError:
        puts(colored.red("HTTPError - 404"))


def main():
    print(__doc__)
    url = load()
    photos = getPhotos(url)
    puts("--------------")
    puts(colored.yellow("Downloading..."))
    puts("--------------")
    for key in progress.bar(photos.keys()):
        name = key.split('.')[0]
        parts = [name[i:i+2] for i in range(0, len(name), 2)]
        folder = os.path.join(parts[0], parts[1], parts)
        if not os.path.exists(folder):
            os.makedirs(folder)
        item = html + photos[key]
        downloadPhoto(folder, item)
        #puts("%s done." % key)
    puts(colored.green("Finished."))


if __name__ == "__main__":
    main()
