from modules.http_client import HttpClient
from modules.auth import Auth
from modules.endpoint_discovery import EndpointDiscovery


# client = HttpClient("https://demo.testfire.net")
# auth = Auth(client, "admin", "admin")
#
# login_success = auth.login()
# print("Logged in:", login_success)
# balance = auth.get_balance()

discovery = EndpointDiscovery("https://demo.testfire.net")
discovery.search()

