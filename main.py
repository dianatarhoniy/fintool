from modules.http_client import HttpClient
from modules.auth import Auth

client = HttpClient("https://demo.testfire.net")
auth = Auth(client, "admin", "admin")

login_success = auth.login()
print("Logged in:", login_success)
balance = auth.get_balance()

