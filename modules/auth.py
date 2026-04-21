import re
class Auth:
    def __init__(self,client,username,password):
        self.client = client
        self.username = username
        self.password = password
    def login(self):
        print(f"Attempting login as {self.username}...")
        response = self.client.post("/doLogin", data =
        {"uid": self.username,
         "passw": self.password,
         "btnSubmit": "Login" })

        if "Sign Off" in response.text:
            return True
        else:
            return False

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



