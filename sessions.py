import requests

import urllib.parse


class BaseUrlSession(requests.Session):
    """A Session with a URL that all requests will use as a base"""

    def __init__(self, base_url, extra_headers=None):
        self.base_url = base_url
        self.extra_headers = extra_headers
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        """Send the request after generating the complete URL."""
        url = urllib.parse.urljoin(self.base_url, url)
        return super().request(
            method, url, headers=self.extra_headers, *args, **kwargs
        )