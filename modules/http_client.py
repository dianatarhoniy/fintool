import requests
class HttpClient:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def get(self, path):
        url = self.url + path
        response = self.session.get(url)
        print(f"[GET] {url} -> {response.status_code}")
        return response

    def post(self, path, data):
        url = self.url + path
        response = self.session.post(url, data=data)
        print(f"[POST] {url} -> {response.status_code}")
        return response
    def get_cookies(self):
        return dict(self.session.cookies)


