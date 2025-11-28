import logging
import os
import requests
logger = logging.getLogger(__name__)

TARGET_URL = os.environ.get('SYSML_API_URL', "http://localhost:9000")

def send_request(method, endpoint, body=None):
    url = f'{TARGET_URL}{endpoint}'

    logger.debug(f'Sending {method} request to {url} with body: {body}')
    response = requests.request(
        method=method, 
        headers={"Content-Type": "application/json"},
        url=url, 
        json=body
    )

    if response.status_code != 200:
        logger.error(f'Request to {url} failed with status code {response.status_code}: {response.text}')

    return response
