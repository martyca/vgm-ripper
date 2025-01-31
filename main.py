#!/usr/bin/env python

import logging
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote_plus
from os.path import split, join
from os import makedirs
import click
import sys

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_url(url):
    """
    Validates the given URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_full_url_from_element(el, url):
    """
    Constructs a full URL from the given element and base URL.

    Args:
        element (bs4.element.Tag): The BeautifulSoup element to extract the URL from.
        base_url (str): The base URL to use for constructing the full URL.

    Returns:
        str: The full URL.
    """
    scheme  = urlparse(url).scheme + '://'
    baseurl = scheme + urlparse(url).netloc
    return baseurl + el.a['href']


def extract_album_name_from_url(url):
    """
    Extracts the album name from the given URL.

    Args:
        url (str): The URL to extract the album name from.

    Returns:
        str: The album name.
    """
    return split(urlparse(url).path)[-1].replace('-', ' ')


def create_directory(directory_path):
    """
    Creates a directory at the given path.

    Args:
        directory_path (str): The path where the directory should be created.
    """
    try:
        makedirs(directory_path)
        logger.info(f"Directory '{directory_path}' created successfully.")
    except FileExistsError:
        logger.warning(f"Directory '{directory_path}' already exists.")
    except OSError as e:
        logger.error(f"Failed to create directory '{directory_path}'. Error: {e}")


def extract_song_pages_from_url(url):
    """
    Extracts song pages from the given URL.

    Args:
        url (str): The URL to extract song pages from.

    Returns:
        map: A map object with the full URLs of the song pages.
    """
    contents = urllib.request.urlopen(url).read()
    soup     = BeautifulSoup(contents, 'html.parser')
    songs    = soup.find_all(class_="playlistDownloadSong")
    logger.info(f"found {len(songs)} songs")
    logger.debug(f"Yielding song pages {songs}")
    return map(lambda el: get_full_url_from_element(el, url), songs)


def get_song_page_content(url, quality):
    """
    Fetches the content of a song page.

    Args:
        url (str): The URL of the song page.
        quality (int): The quality of the song (0 for low quality, -1 for high quality).

    Returns:
        str: The content of the song page.
    """
    contents = urllib.request.urlopen(url).read()
    soup     = BeautifulSoup(contents, 'html.parser')
    link     = soup.find_all(class_="songDownloadLink")[quality].parent['href']
    logger.debug("Yielding song link {}".format(link))
    return link


def get_remote_file_length(url):
    """
    Gets the length of a remote file.

    Args:
        url (str): The URL of the remote file.

    Returns:
        int: The length of the remote file.
    """
    return urllib.request.urlopen(url).length


def download_song(url, path):
    """
    Downloads a song from the given URL and saves it to the given path.

    Args:
        url (str): The URL of the song.
        path (str): The path where the song should be saved.
    """
    filename = unquote_plus(split(urlparse(url).path)[-1])
    logger.info(f"Downloading {filename}")
    urllib.request.urlretrieve(url, join(path, filename))


@click.command(no_args_is_help=True)
@click.argument('url')
@click.option('--quality', type=click.Choice(['high', 'low'], case_sensitive=False), default='low', help='Set the quality of the music file to download (low = mp3, high = flac), defaults to low.')
def main(url, quality):
    """
    The main function of the script. Validates the given URL, creates a directory for the album, 
    extracts song pages from the URL, and downloads each song.

    Args:
        url (str): The URL of the album.
        quality (str): The quality of the songs to download ('high' or 'low').
    """
    quality = -1 if quality == "high" else 0

    # validation
    if not validate_url(url):
        sys.exit(f"not a valid url {url}, exiting!")
    # create dir
    album_name = extract_album_name_from_url(url)
    create_directory(f"/downloads/{album_name}")
    for i in extract_song_pages_from_url(url):
        download_song(get_song_page_content(i, quality), f"/downloads/{album_name}")


if __name__ == "__main__":
    main()