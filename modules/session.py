import base64
import re

from modules.finding import Finding


class SessionTesting:
    def __init__(self,client,auth,config):
        self.client = client
        self.auth = auth
        self.config = config

    def check_flags(self):
        print("\n[1] Checking cookie security flags...")
        findings = []

        cookies = self.auth.header
        if not cookies:
            print("    [ERROR] No Set-Cookie header captured")
            return findings
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
                findings.append(Finding(
                    check="Session",
                    severity="MEDIUM",
                    title=f"Cookie {name} missing HttpOnly flag",
                    evidence=f"Cookie {name} has no HttpOnly attribute; readable by JavaScript"
                ))

            if has_secure:
                print(f"        [SAFE]       Secure present")
            else:
                print(f"        [VULNERABLE] Missing Secure - sent over plain HTTP")
                findings.append(Finding(
                    check="Session",
                    severity="MEDIUM",
                    title=f"Cookie {name} missing Secure flag",
                    evidence=f"Cookie {name} has no Secure attribute; can be sent over plain HTTP"
                ))

            if has_samesite:
                print(f"        [SAFE]       SameSite present")
            else:
                print(f"        [VULNERABLE] Missing SameSite - CSRF attacks possible")
                findings.append(Finding(
                    check="Session",
                    severity="MEDIUM",
                    title=f"Cookie {name} missing SameSite flag",
                    evidence=f"Cookie {name} has no SameSite attribute; vulnerable to CSRF"
                ))
        return findings
    def check_data_leaks(self):
        print("\n[2] Checking data leaks...")
        findings = []
        cookies = self.client.get_cookies()

        for name, value in cookies.items():
            print(f"    Cookie: {name}")
            print(f"    Value: {value[:30]}")

            try:
                decoded = base64.b64decode(value, validate=True).decode("utf-8")
                print(f" Decoded cookie: {decoded}")
                if re.search(r'\d{6,}', decoded):
                    print(f"    [VULNERABLE]       Account number leak present")
                    findings.append(Finding(
                        check="Session",
                        severity="HIGH",
                        title=f"Account number leaked in cookie {name}",
                        evidence=f"Cookie {name} decodes to data containing an account number"
                    ))

                if re.search(r'\d+\.\d{2}', decoded):
                    print(f"    [VULNERABLE]       Balance leak present")
                    findings.append(Finding(
                        check="Session",
                        severity="HIGH",
                        title=f"Balance leaked in cookie {name}",
                        evidence=f"Cookie {name} decodes to data containing a balance amount"
                    ))

            except Exception:
                print(f"    [INFO] Not base64 decoded")

        return findings

    def check_session_after_logout(self):
        print("\n[3] Checking if session is valid after logout...")
        findings = []

        # Step 1 - save the session ID before logout
        old_jsessionid = self.client.get_cookies().get(self.config["cookie_name"])
        if not old_jsessionid:
            print("    [ERROR] No JSESSIONID found before logout")
            return findings
        print(f"    Session ID before logout: {old_jsessionid}")

        # Step 2 - logout
        self.auth.logout()
        print("    Logged out.")

        # Step 3 - put the old cookie back
        self.client.session.cookies.set(self.config["cookie_name"], old_jsessionid)
        print(f"    Replaying old session ID: {old_jsessionid}")

        # Step 4 - try to access a protected page
        response = self.client.get(self.config["protected_page"])

        # Step 5 - check if we got in
        if self.config["success_marker"] in response.text:
            print("    [VULNERABLE] Old session still works after logout!")
            print("    An attacker who stole this cookie can still access the account.")
            findings.append(Finding(
                check="Session",
                severity="HIGH",
                title="Session still valid after logout",
                evidence="The old JSESSIONID still reaches an authenticated page after logout"
            ))
        else:
            print("    [SAFE] Session correctly invalidated after logout.")
        return findings

    def run(self):
        findings = []
        findings += self.check_flags()
        findings += self.check_data_leaks()
        findings += self.check_session_after_logout()

        if not findings:
            findings.append(Finding(
                check="Session",
                severity="SAFE",
                title="No session or cookie issues found",
                evidence="All cookies had secure flags, no data leaks, and the session was invalidated after logout"
            ))
        return findings