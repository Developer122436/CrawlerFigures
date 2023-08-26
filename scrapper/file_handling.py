import os
from urllib.parse import urlparse

import requests


def download_file(url, destination, cookie):
    """
    Download a file from the specified URL and save it to the provided destination.

    :param url: The URL of the file to download.
    :param destination: The path where the file should be saved.
    :param cookie: The cookies for accessing the file
    """

    # Extract the base file name from the URL
    file_name = os.path.basename(urlparse(url).path)

    # Join the destination path with the file name
    destination = os.path.join(destination, file_name)

    # Define request headers, including User-Agent and Cookie for the request
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        'Cookie': f"__cf_bm={cookie}",
    }

    # Send a GET request to the provided URL with the headers
    response = requests.get(url, headers=headers)

    # Check if the HTTP response indicates an error, and if so, raise an exception
    response.raise_for_status()

    # Save the content of the response to the destination file in chunks
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def create_dir(path):
    """
    Create a directory
    :param path: The path of the directory
    """

    # If the directory does not exist, then it is created. If it already exists, this function does nothing.
    if not os.path.exists(path):
        os.makedirs(path)
