import requests

class HttpClient:
    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path, **kwargs):
        url = self.url + path
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.get(url, **kwargs)
        print(f"[GET] {url} -> {response.status_code}")
        return response

    def post(self, path, data, **kwargs):
        url = self.url + path
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.post(url, data=data, **kwargs)
        print(f"[POST] {url} -> {response.status_code}")
        return response

    def get_cookies(self):
        return dict(self.session.cookies)