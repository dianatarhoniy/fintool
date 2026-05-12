import base64
import re

class SessionTesting:
    def __init__(self,client,auth):
        self.client = client
        self.auth = auth

    def check_flags(self):
        print("\n[1] Checking cookie security flags...")

        raw = self.auth.header
        if not raw:
            print("    [ERROR] No Set-Cookie header captured")
            return

        print(f"    Raw header: {raw}\n")

        # Each cookie is separated by ", "
        cookies = raw.split(", ")

        for cookie in cookies:
            # Get just the name before the first "="
            name = cookie.split("=")[0].strip()
            cookie_lower = cookie.lower()

            print(f"    Cookie: {name}")

            if "httponly" in cookie_lower:
                print(f"        [SAFE]       HttpOnly present")
            else:
                print(f"        [VULNERABLE] Missing HttpOnly - JavaScript can steal this cookie")

            if "secure" in cookie_lower:
                print(f"        [SAFE]       Secure present")
            else:
                print(f"        [VULNERABLE] Missing Secure - sent over plain HTTP")

            if "samesite" in cookie_lower:
                print(f"        [SAFE]       SameSite present")
            else:
                print(f"        [VULNERABLE] Missing SameSite - CSRF attacks possible")
            print()
    def check_data_leaks(self):
        print("\n[2] Checking data leaks...")
        cookies = self.client.get_cookies()

        for name, value in cookies.items():
            print(f"    Cookie: {name}")
            print(f"    Value: {value[:30]}")

            try:
                decoded = base64.b64decode(value).decode()
                print(f" Decoded cookie: {decoded}")
                if re.search(r'\d{6,}', decoded):
                    print(f"    [VULNERABLE]       Account number leak present")

                if re.search(r'\d+\.\d{2}', decoded):
                    print(f"    [VULNERABLE]       Balance leak present")

            except Exception:
                print(f"    [INFO] Not base64 decoded")

    def check_session_after_logout(self):
        print("\n[3] Checking if session is valid after logout...")

        # Step 1 - save the session ID before logout
        old_jsessionid = self.client.get_cookies().get("JSESSIONID")
        print(f"    Session ID before logout: {old_jsessionid}")

        # Step 2 - logout
        self.auth.logout()
        print("    Logged out.")

        # Step 3 - put the old cookie back
        self.client.session.cookies.set("JSESSIONID", old_jsessionid)
        print(f"    Replaying old session ID: {old_jsessionid}")

        # Step 4 - try to access a protected page
        response = self.client.get("/bank/main.jsp")

        # Step 5 - check if we got in
        if "Sign Off" in response.text:
            print("    [VULNERABLE] Old session still works after logout!")
            print("    An attacker who stole this cookie can still access the account.")
        else:
            print("    [SAFE] Session correctly invalidated after logout.")






