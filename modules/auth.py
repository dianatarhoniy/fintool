import re


def attempt_login(client, uid, passw):
    response = client.post(
        "/doLogin",
        data={
            "uid": uid,
            "passw": passw,
            "btnSubmit": "Login"
        },
        allow_redirects=False
    )
    set_cookie_headers = response.raw.headers.getlist("Set-Cookie")

    if response.status_code != 302:
        return False, set_cookie_headers

    location = response.headers.get("Location", "/bank/main.jsp")
    if location.startswith("/altoromutual"):
        location = location.replace("/altoromutual", "", 1)

    dashboard = client.get(location)
    return "Sign Off" in dashboard.text, set_cookie_headers


class Auth:
    def __init__(self,client,username,password):
        self.client = client
        self.username = username
        self.password = password
        self.header = None

    def login(self):
        print(f"Attempting login as {self.username}...")
        success, self.header = attempt_login(self.client, self.username, self.password)
        if success:
            print("[AUTH] Login successful.")
        else:
            print("[AUTH] Login failed.")
        return success


    def logout(self):
        print(f"Attempting logout as {self.username}...")
        response = self.client.get("/logout.jsp")
        return response

    def get_balance(self, account="800002"):
        response = self.client.get(f"/bank/showAccount?listAccounts={account}")
        if "Balance Detail" in response.text:
            match = re.search(r'Ending balance.*?<td align="right">(.*?)</td>', response.text, re.DOTALL)
            if match:
                balance = match.group(1).strip()
                print(f"[AUTH] Balance for account {account}: {balance}")
                return balance
        print("[AUTH] Could not get balance!")
        return None



