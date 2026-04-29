import base64

import requests

from modules.double_spending import DoubleSpending
from modules.http_client import HttpClient
from modules.auth import Auth
from modules.endpoint_discovery import EndpointDiscovery
from modules.idor import IDOR
# discovery = EndpointDiscovery("https://demo.testfire.net")
# discovery.search()
client = HttpClient("http://localhost:8080/altoromutual")
auth = Auth(client, "jsmith", "demo1234")

login_success = auth.login()
print("Logged in:", login_success)
print(client.get_cookies())


#balance = auth.get_balance()


#d = DoubleSpending(client,auth)
#d.run()

#idor = IDOR(client,auth)
#idor.run()







