import base64
import re

class SessionTesting:
    def __init__(self,client,auth):
        self.client = client
        self.auth = auth

    def check_flags(self):
        print("\n[1] Checking cookie security flags...")

        cookies = self.auth.header
        if not cookies:
            print("    [ERROR] No Set-Cookie header captured")
            return
        for cookie in cookies:
            parts = [part.strip() for part in cookie.split(";")]
            name = parts[0].split("=")[0].strip()
            attributes = [part.lower() for part in parts[1:]]

            has_httponly = "httponly" in attributes
            has_secure = "secure" in attributes
            has_samesite = any(part.startswith("samesite") for part in attributes)

            print(f"    Cookie: {name}")

            if has_httponly:
                print(f"        [SAFE]       HttpOnly present")
            else:
                print(f"        [VULNERABLE] Missing HttpOnly - JavaScript can steal this cookie")

            if has_secure:
                print(f"        [SAFE]       Secure present")
            else:
                print(f"        [VULNERABLE] Missing Secure - sent over plain HTTP")

            if has_samesite:
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
                decoded = base64.b64decode(value, validate=True).decode("utf-8")
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
        if not old_jsessionid:
            print("    [ERROR] No JSESSIONID found before logout")
            return
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