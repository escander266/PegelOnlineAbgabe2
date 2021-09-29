# -*- coding: utf-8 -*-
import os
import gzip
import json
from urllib import request
import urllib.parse
import urllib.error


def quote(string_to_quote):
    return urllib.parse.quote(string_to_quote)

class Urlreader(object):

    def __init__(self, url):

        self.url = url
        self.block_sz = 8192
        self.code = 0
        self.headers = None


    def _openURL(self):
        """Send a request to url, return the response"""
        try:
            rq = request.Request(self.url)
            rq.add_header('Accept-Encoding', 'gzip')
            response = request.urlopen(rq)
            self.code = response.code
            self.headers = dict(response.headers)
            return response

        except urllib.error.HTTPError as e:
            print ("HTTP error reading url:", self.url)
            print ("Code", e.code, e.msg)
            self.code = e.code
            #print ("Returns", e.read())

        except urllib.error.URLError as e:
            print ("URL error reading url:", self.url)
            print ("Reason:", e.reason)

        return None


    def getDataResponse(self):
        """download into data buffer"""

        data = b""
        response = self._openURL()

        if not response:
            return data

        if response.headers['Content-Encoding'] == 'gzip':
            data = gzip.GzipFile(fileobj=response).read()
        else:
            data = response.read()

        return data

    def getJsonResponse(self):
        """load a json structure from a REST-URL, returns a list/dict python object"""

        data = self.getDataResponse()
        if data is None or data == b"":
            return None

        d = json.loads(data)
        return d

    def getFileResponse(self, dest):
        """read response from url, save it to dest/filename,
        returns the dest/filename.
        dest should be a directory
        filename is derived from url
        """

        data = self.getDataResponse()
        if data is None or data == b"":
            return None

        # get file name from url
        result = urllib.parse.urlparse(self.url)
        file_name = os.path.basename(
            result.path if len(result.path) > 0 else result.hostname
        )

        # join with destination dir
        file_name = os.path.realpath(os.path.join(dest, file_name))
        # open, write and close
        savefile = open(file_name, 'wb')
        savefile.write(data)
        savefile.close()
        # return saved file name
        return file_name

if __name__ == '__main__':
    #url = "https://www.uni-trier.de"
    #url = "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json"
    # url = 'http://www.python.org/fish.html'
    url = "https://www.pegelonline.wsv.de/img/wsv_rgb_m.jpg"
    #url = "https://download.osgeo.org/osgeo4w/x86/setup_test.ini.bz2"
    #url = "https://wiki.mozilla.org/images/f/ff/Example.json.gz"
    # result = request.urlopen(url)
    #
    # result = openURL(url)
    ur = Urlreader(url)
    result = ur.getDataResponse()
    # result = ur.getJsonResponse()
    print(ur.code)
    #result = ur.getFileResponse("c:/temp")
    # print (result)
