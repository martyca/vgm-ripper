import logging
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote_plus
from os.path import split, join
from os import makedirs
import argparse
import sys

parser = argparse.ArgumentParser(description="Downloads mp3's from https://downloads.khinsider.com.")
parser.add_argument("url")
parser.add_argument('--quality', choices=['high', 'low'], default='low', help='Set the quality of the music file to download (low = mp3, high = flac), defaults to low.')
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url     = args.url
quality = -1 if args.quality == "high" else 0
def validate_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

def return_href(el):
    scheme  = urlparse(url).scheme + '://'
    baseurl = scheme + urlparse(url).netloc
    return baseurl + el.a['href']

def return_album_name(url):
    return split(urlparse(url).path)[-1].replace('-', ' ')

def create_directory(directory_path):
    logger = logging.getLogger(__name__)
    try:
        makedirs(directory_path)
        logger.info(f"Directory '{directory_path}' created successfully.")
    except FileExistsError:
        logger.warning(f"Directory '{directory_path}' already exists.")
    except OSError as e:
        logger.error(f"Failed to create directory '{directory_path}'. Error: {e}")

def return_song_pages(url):
    contents = urllib.request.urlopen(url).read()
    soup     = BeautifulSoup(contents, 'html.parser')
    songs    = soup.find_all(class_="playlistDownloadSong")
    logger.info(f"found {len(songs)} songs")
    logger.debug(f"Yielding song pages {songs}")
    return map(return_href, songs)

def return_song_link(url):
    contents = urllib.request.urlopen(url).read()
    soup     = BeautifulSoup(contents, 'html.parser')
    link     = soup.find_all(class_="songDownloadLink")[quality].parent['href']
    logger.debug("Yielding song link {}".format(link))
    return link

def get_remote_file_length(url):
    return urllib.request.urlopen(url).length

def download_song(url, path):
    filename = unquote_plus(split(urlparse(url).path)[-1])
    logger.info(f"Downloading {filename}")
    urllib.request.urlretrieve(url, join(path, filename))

if __name__ == "__main__":
    # validation
    if not validate_url(url):
        sys.exit("not a valid url {}, exiting!".format(url))
    # create dir
    album_name = return_album_name(url)
    create_directory(album_name)
    for i in return_song_pages(url):
        download_song(return_song_link(i), album_name)


