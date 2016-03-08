import logging
from urllib.request import urlopen
from shutil import copyfileobj

class MapDownloader(object):

    def __init__(self):

        self.__log = logging.getLogger(__name__)

    def to_file(self, top, left, bottom, right, file_path = 'map.osm'):

        self.__log.info('Downloading map data for [%f,%f,%f,%f]' % (top, left, bottom, right))
        url = 'http://www.overpass-api.de/api/xapi?way[bbox=%f,%f,%f,%f][highway=*]' % (left, bottom, right, top)

        with urlopen(url) as response, open(file_path, 'wb') as out_file:
            copyfileobj(response, out_file)

        self.__log.info('Download complete, saved as %s' % file_path)
